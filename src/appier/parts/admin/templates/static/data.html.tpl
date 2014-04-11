{% extends "partials/layout.static.html.tpl" %}
{% block title %}Data{% endblock %}
{% block name %}Data{% endblock %}
{% block content %}
    <div class="quote">Data</div>
    <div class="separator-horizontal"></div>
    <div class="lchart">
        <div class="data">
            {
                "labels" : ["first", "second"]
                "values" : [[1, 2], [4, 5], [6, 4], [4, 6]]
            }
        </div>
    </div>
{% endblock %}
