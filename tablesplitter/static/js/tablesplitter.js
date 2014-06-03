(function(window, $, _, Backbone, TableSplitter) {
  window.TableSplitter = TableSplitter;

  var BaseCollection = Backbone.Collection.extend({
    parse: function(response) {
      return response.objects;
    }
  });

  var Cells = TableSplitter.Cells = BaseCollection.extend({
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
