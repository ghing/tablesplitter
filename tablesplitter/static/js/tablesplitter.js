(function(window, $, _, Backbone, TableSplitter) {
  window.TableSplitter = TableSplitter;

  var KEYCODE_ESC = 27;
  var KEYCODE_N = 110;
  var KEYCODE_P = 112;

  // Models

  var Cell = TableSplitter.Cell = Backbone.Model.extend();

  var Text = Backbone.Model.extend({
    url: function() {
      var collectionUrl = _.result(this.collection, 'url');
      var url = collectionUrl.split('?')[0];
      if (this.id) {
        url = url + this.id + '/';  
      }
      return url; 
    }
  });

  // Collections

  var BaseCollection = Backbone.Collection.extend({
    parse: function(response) {
      return response.objects;
    }
  });

  var Cells = TableSplitter.Cells = BaseCollection.extend({
    model: Cell,

    url: function() {
      var url = '/api/cells/';
      var queryParams = _.pick(this.options, 'limit', 'text_lt', 'random', 'no_accepted');
      
      if (!_.isEmpty(queryParams)) {
        url += '?'; 
      }

      _.each(queryParams, function(val, key) {
        url += key + "=" + val + "&";
      });
      
      return url;
    },

    initialize: function(models, options) {
      this.options = _.extend({}, options);
    }
  });

  var Texts = TableSplitter.Texts = BaseCollection.extend({
    model: Text,

    url: function() {
      var url = '/api/text/';
      if (this.options.imageId) {
        url = url + "?image_file=" + this.options.imageId; 
      }
      return url;
    },

    initialize: function(models, options) {
      this.options = options || {};
    }
  });

  // View

  var CellImageView = TableSplitter.CellImageView = Backbone.View.extend({
    className: 'cell-entry-img',

    initialize: function(options) {
      this.collection.on('sync', this.render, this);
    },

    render: function() {
      var cell;

      this.$el.empty();

      if (!this.collection.length) {
        $("<p>There are no more images</p>").appendTo(this.$el);
      }
      else {
        cell = this.collection.at(0);
        $('<img>').attr('src', cell.get('image_url'))
          .appendTo(this.$el);
      }

      return this;
    }
  });

  var TranscriptionFormView = TableSplitter.TranscriptionFormView = Backbone.View.extend({
    tagName: 'form',

    attributes: {
      'role': 'form'
    },

    events: {
      'submit': 'handleSubmit'
    },

    initialize: function() {
      this.collection.on('sync', this.updateModel, this);
      this.texts = new Texts();
    },

    render: function() {
      var formHtml = '<div class="form-group">' +
        '<label for="text">Enter cell text</label>' +
        '<input name="text" id="text" type="text" class="form-control">' +
        '</div>' +
        '<button type="submit">Submit</button>'; 
      $(formHtml).appendTo(this.$el);
      return this;
    },

    handleSubmit: function(evt) {
      evt.preventDefault();

      if (!this.model) {
        return;
      }

      var text = $('#text').val();

      var textObj = this.texts.create({
        source: this.model.id,
        method: 'manual',
        text: text,
        user_id: ''
      });

      textObj.once('sync', function() {
        this.$('#text').val('');
        this.collection.fetch();
      }, this);
    },

    updateModel: function() {
      if (this.collection.length) {
        this.model = this.collection.at(0);
      }
      else {
        this.model = null;
        this.toggleDisabled();
      }
    },

    toggleDisabled: function() {
      var disabled = this.model ? false : true;
      this.$('button').prop('disabled', disabled);
      return this;
    }
  });

  TableSplitter.AcceptTextView = Backbone.View.extend({
    events: {
      'click .btn-accept': 'clickAccept'
    },

    initialize: function() {
      this.model.on('sync', this.render, this);
    },

    render: function() {
      if (this.model.get('accepted')) {
        this.$('.btn-accept').hide();
        if (!this.$('.label-success').length) {
          $('<span class="label label-success">Accepted</span>').appendTo(this.$el);
        }
      }
      return this;
    },

    clickAccept: function(evt) {
      evt.preventDefault();
      this.model.set('accepted', true);
      this.model.save();
    }
  });

  /**
   * View for editing an individual text version from the image file page.
   */
  TableSplitter.EditTextView = Backbone.View.extend({
    options: {
      formHtml: '<form><input type="text"></input></form>'
    },

    events: {
      'click .cell-text-value': 'handleClickText',
      'submit form': 'handleSubmit',
      'blur form': 'handleBlur'
    },

    initialize: function() {
      this._editing = false;
      $(window).on('keyup', _.bind(this.handleKeyup, this));
      this.render();
    },

    render: function() {
      var displayText = this.model.get('text') == "" ? "(Empty)" : this.model.get('text');

      if (this.$('form').length == 0) {
        $(this.options.formHtml).hide().insertAfter(this._getTextEl());
      }
      this._getForm().find('input[type="text"]').val(this.model.get('text'));
      this._getTextEl().html(displayText);
      
      if (this._editing) {
        this._getTextEl().hide();
        this._getForm().show();
      }
      else {
        this._getTextEl().show();
        this._getForm().hide();
      }

      return this;
    },

    _getTextEl: function() {
      return this.$('.cell-text-value');
    },

    _getForm: function() {
      return this.$('form');
    },

    _startEdit: function() {
      this._editing = true;
      Backbone.trigger('edit:text:start', this.model);
      this.render();
    },

    _endEdit: function() {
      this._editing = false;
      Backbone.trigger('edit:text', this.model);
      this.render();
    },

    handleClickText: function(evt) {
      this._startEdit();
      this._getForm().find('input[type="text"]').focus();
    },

    handleSubmit: function(evt) {
      evt.preventDefault();
      var val = this._getForm().find('input[type="text"]').val();
      this.model.set('text', val);
      this.model.save();
      this._endEdit();
    },

    handleBlur: function(evt) {
      this._endEdit();
    },

    handleKeyup: function(evt) {
      if (this._editing && evt.keyCode === KEYCODE_ESC) {
        this._endEdit();
      }
    }
  });

  TableSplitter.CellView = Backbone.View.extend({
    events: {
      'click': 'handleClick',
    },

    initialize: function() {
      this._selected = false;
      Backbone.on('select:cell', this.handleSelectCell, this);
    },

    render: function() {
      this.$el.toggleClass('selected', this._selected);
      return this;
    },

    handleSelectCell: function(id) {
      this._selected = this.model.id === id;
      this.render();
    },

    handleClick: function(evt) {
      if (!this._selected) {
        Backbone.trigger('select:cell', this.model.id);
      }
    },
  });

  TableSplitter.CellNavigationView = Backbone.View.extend({
    initialize: function() {
      this._editingText = false;
      this._selectedCellId = null;
      $(window).on('keypress', _.bind(this.handleKeypress, this));
      Backbone.on('select:cell', this.handleSelectCell, this);
      Backbone.on('edit:text:start', this.handleStartEditText, this);
      Backbone.on('edit:text', this.handleEditText, this);
    },

    handleSelectCell: function(id) {
      this._selectedCellId = id;
      this._$cellEl = this._getCellEl(id);
    },

    handleKeypress: function(evt) {
      var $nextEl, nextId, pos;

      if (evt.which === KEYCODE_N && !this._editingText) {
        this._switchToCell(this._getNextEl());
      }
      else if (evt.which === KEYCODE_P && !this._editingText) {
        this._switchToCell(this._getPrevEl());
      }
    },

    _switchToCell: function($el) {
      var pos;

      if ($el && $el.length) {
        Backbone.trigger('select:cell', $el.data('id'));
        pos = $el.position();
        window.scrollTo(0, pos.top);
      }
    },

    _getCellEl: function(id) {
      return this.$('#cell-' + id);
    },

    _getPrevEl: function() {
      if (this._$cellEl) {
        return this._$cellEl.prev('.cell');
      }
      else {
        return null;
      }
    },

    _getNextEl: function() {
      if (this._$cellEl) {
        return this._$cellEl.next('.cell');
      }
      else {
        return null;
      }
    },

    handleStartEditText: function() {
      this._editingText = true;
    },

    handleEditText: function() {
      this._editingText = false;
    }
  });

  TableSplitter.App = function(options) {
    this.collection = new Cells(null, {
      limit: 1,
      text_lt: 3,
      random: true,
      no_accepted: true
    });

    this.imgView = new CellImageView({collection: this.collection});
    this.formView = new TranscriptionFormView({collection: this.collection});
    options.el.append(this.imgView.$el);
    options.el.append(this.formView.render().$el);
    this.collection.fetch();
  };
})(window, jQuery, _, Backbone, window.TableSplitter || {});
