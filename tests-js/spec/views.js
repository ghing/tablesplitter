// Use Mustache-style templates for _.template()
_.templateSettings = {
  interpolate: /\{\{(.+?)\}\}/g
};

describe("EditTextView", function() {
  var html = '<li class="cell-text" data-id="1"><pre class="cell-text-value">(Empty)</pre></li>';
  var $el;
  var model;
  var view;

  beforeEach(function() {
    $el = $(html);
    $('body').append($el);
    model = new Backbone.Model({
      'id': 1,
      'text': '',
      'accepted': false,
      'source': 1
    });
    spyOn(model, 'save');
    view = new TableSplitter.EditTextView({
      el: $el,
      model: model
    });
  });

  afterEach(function() {
    $el.remove();
  });

  it("adds a text input to the element when initialized", function() {
    expect($el.find('input[type="text"]').length).toEqual(1);
    expect($el.find('input[type="text"]:visible').length).toEqual(0);
  });

  it("shows a text input and sets focus to it when the text is clicked", function() {
    $el.find('.cell-text-value').trigger('click');
    expect($el.find('input[type="text"]:visible').length).toEqual(1);
    expect($el.find('.cell-text-value').css('display')).toEqual('none');
    expect($el.find('input[type="text"]').is(':focus')).toBeTruthy();
  });

  it("saves the model with updated text and hides the form when the form is submitted", function() {
    var textVal = "New Text";
    var $input = $el.find('input[type="text"]');
    $el.find('.cell-text-value').trigger('click');
    $input.val(textVal);
    // It would be nice to test on an enter keypress in the input, but that's
    // annoying to try to simulate in a way that will create a form submit.
    $el.find('form').trigger('submit');
    expect(model.save).toHaveBeenCalled();
    expect(model.get('text')).toEqual(textVal);
    expect($el.find('form:visible').length).toEqual(0);
    expect($el.find('.cell-text-value').html()).toEqual(textVal);
  });

});

describe('CellView', function() {
  var tpl = '<li class="cell" id="cell-{{ id }}">';
  var spy, $el, model, view;

  beforeEach(function() {
    spy = jasmine.createSpy("eventSpy");
    model = new Backbone.Model({
      'id': 1,
    });
    $el = $(_.template(tpl, {id: model.id}));
    $('body').append($el);
    view = new TableSplitter.CellView({
      el: $el,
      model: model
    });
  });

  afterEach(function() {
    $el.remove();
  });

  it("emits an event and sets a class when clicked", function() {
    Backbone.on('select:cell', spy);
    $el.trigger('click');
    expect($el.hasClass('selected')).toBeTruthy();
    expect(spy).toHaveBeenCalledWith(model.id);
  });
});
