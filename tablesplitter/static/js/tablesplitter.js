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
      var queryParams = _.pick(this.options, 'limit', 'text_lt', 'random');
      
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
    url: '/api/text/'
  });

  var CellImageView = TableSplitter.CellImageView = Backbone.View.extend({
    tagName: 'img',

    initialize: function(options) {
      this.collection.on('sync', this.render, this);
    },

    render: function() {
      var cell = this.collection.at(0);
      this.$el.attr('src', cell.get('image_url'));
      return this;
    }
  });

  var TranscriptionFormView = TableSplitter.TranscriptionFormView = Backbone.View.extend({
    tagName: 'form',

    events: {
      'submit': 'handleSubmit'
    },

    initialize: function() {
      this.collection.on('sync', this.updateModel, this);
      this.texts = new Texts();
    },

    render: function() {
      $('<input name="text" id="text" type="text">').appendTo(this.$el);
      $('<button type="submit">Submit</button>').appendTo(this.$el);
      return this;
    },

    handleSubmit: function(evt) {
      evt.preventDefault();

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
      // @todo: Handle case when there are no more available items
      this.model = this.collection.at(0);
    }
  });

  TableSplitter.App = function(options) {
    this.collection = new Cells(null, {
      limit: 1,
      text_lt: 3,
      random: true
    });

    this.imgView = new CellImageView({collection: this.collection});
    this.formView = new TranscriptionFormView({collection: this.collection});
    options.el.append(this.imgView.$el);
    options.el.append(this.formView.render().$el);
    this.collection.fetch();
  };
})(window, jQuery, _, Backbone, window.TableSplitter || {});
