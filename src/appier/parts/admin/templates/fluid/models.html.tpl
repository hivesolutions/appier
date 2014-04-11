{% extends "partials/layout.fluid.html.tpl" %}
{% block title %}Show{% endblock %}
{% block name %}Show{% endblock %}
{% block style %}no-header{% endblock %}
{% block buttons %}
    {{ super() }}
    <div class="button button-color button-grey" data-link="{{ url_for('form') }}">Edit</div>
{% endblock %}
{% block content %}
    <div class="show-panel">
        	<ul>
		{% for model in models %}
			<li>{{ model }}</li>
		{% endfor %}
	</ul>
    </div>
{% endblock %}
