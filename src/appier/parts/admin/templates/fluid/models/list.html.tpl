{% extends "partials/layout.fluid.html.tpl" %}
{% block title %}Models{% endblock %}
{% block name %}Models{% endblock %}
{% block style %}no-header{% endblock %}
{% block content %}
    <div class="show-panel">
        <ul>
            {% for model in models %}
                <li>{{ model._name() }}</li>
            {% endfor %}
        </ul>
    </div>
{% endblock %}
