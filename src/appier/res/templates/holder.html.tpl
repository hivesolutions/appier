{% extends "layout.html.tpl" %}
{% block title %}
    Appier
{% endblock %}
{% block content %}
    <div class="message">
        <div class="header">
            <h1>Welcome to Appier Framework</h1>
            <p>You've just configured <strong>{{ owner.description }}</strong> correctly, now it's time to start the development.</p>
        </div>
    </div>
{% endblock %}
