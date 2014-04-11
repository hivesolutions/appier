{% extends "partials/layout.static.html.tpl" %}
{% block title %}Models{% endblock %}
{% block name %}Models{% endblock %}
{% block content %}
	<ul>
		{% for model in models %}
			<li>{{ model }}</li>
		{% endfor %}
	</ul>
{% endblock %}
