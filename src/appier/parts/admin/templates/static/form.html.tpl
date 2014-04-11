{% extends "partials/layout.static.html.tpl" %}
{% block title %}Form{% endblock %}
{% block name %}Form{% endblock %}
{% block content %}
    <form action="{{ url_for('form_action') }}" method="post" class="form">
        <div class="label">
            <label>Name</label>
        </div>
        <div class="input">
            <input name="name" class="text-field focus" placeholder="eg: John Doe" value="{{ form.name }}"
                   data-error="{{ errors.name }}" />
        </div>
        <div class="label">
            <label>Birthday</label>
        </div>
        <div class="input">
            <input name="birthday" type="text" class="text-field" data-type="date"
                   placeholder="yyyy/mm/dd" value="{{ form.birthday }}" data-error="{{ errors.birthday }}" />
        </div>
        <div class="label">
            <label>Place</label>
        </div>
        <div class="input">
            <div name="place" class="drop-field" data-error="{{ errors.place }}">
                <div class="data-source" data-type="countries"></div>
            </div>
        </div>
        <div class="label">
            <label>Country</label>
        </div>
        <div class="input">
            <div name="country" class="drop-field drop-field-select" data-error="{{ errors.country }}"
                 data-number_options="-1">
                <div class="data-source" data-type="countries"></div>
            </div>
        </div>
        <div class="label">
            <label>Related</label>
        </div>
        <div class="input">
            <div name="related" class="tag-field" data-error="{{ errors.related }}">
                <ul class="tags">
                    {% for related in form.related %}
                        <li>{{ related }}</li>
                    {% endfor %}
                </ul>
                <ul class="data-source" data-type="countries"></ul>
            </div>
        </div>
        <div class="label">
            <label>Gender</label>
        </div>
        <div class="input left">
            <input type="radio" name="gender" id="male" value="male" checked="1" />
            <label class="radio-label" for="male">Male</label>
            <input type="radio" name="gender" id="female" value="female" />
            <label class="radio-label" for="female">Female</label>
        </div>
        <div class="panel-more" data-more="more" data-less="less">
            <div class="label">
                <label>Questions</label>
            </div>
            <div class="input">
                <div class="option">
                    <span class="float-left">Do you have a private car for yourself ?</span>
                    <input class="float-right" type="checkbox" name="car" checked="1" />
                    <div class="clear"></div>
                </div>
                <div class="option">
                    <span class="float-left">What about a motocycle for a run ?</span>
                    <input class="float-right" type="checkbox" name="car" />
                    <div class="clear"></div>
                </div>
                <div class="option">
                    <span class="float-left">Born In Passadena ?</span>
                    <input class="float-right" type="checkbox" name="car" />
                    <div class="clear"></div>
                </div>
            </div>
        </div>
        <div class="label">
            <label>Rating</label>
        </div>
        <div class="input">
            <div class="rating" data-name="rating" data-count="5" data-value="{{ form.rating }}"
                 data-error="{{ errors.rating }}"></div>
        </div>
        <div class="label">
            <label>Description</label>
        </div>
        <div class="input">
            <textarea name="description" class="text-area" placeholder="eg: some words about the form"
                      data-error="{{ errors.description }}">{{ form.description }}</textarea>
        </div>
        <table class="table table-edit" data-error="{{ errors.prices }}">
            <input name="prices[]" type="hidden" class="table-empty-field" />
            <thead>
                <tr>
                    <th class="longer-input" data-width="384">Country</th>
                    <th data-width="80">Qty</th>
                    <th data-width="80">Price</th>
                </tr>
            </thead>
            <tbody>
                <tr class="template">
                    <td>
                        <div name="prices[][country]" class="drop-field drop-field-select">
                            <div class="data-source" data-type="countries"></div>
                        </div>
                    </td>
                    <td>
                        <input type="text" name="prices[][quantity]" class="text-field text-right" data-type="floatp" value="1" />
                    </td>
                    <td>
                        <input type="text" name="prices[][price]" class="text-field text-right" data-type="floatp" data-decimal_places="2" />
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <td class="table-new-line-row">
                        <span class="button table-new-line">Add Line</span>
                    </td>
                </tr>
            </tfoot>
        </table>
        <div class="quote">
            By clicking Submit Form, you agree to our Service Agreement and that you have
            read and understand our Privacy Policy.
        </div>
        <span class="button" data-submit="true">Submit Form</span>
    </form>
{% endblock %}
