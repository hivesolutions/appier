{% extends "layout.html.tpl" %}
{% block title %}
    {% if own.is_devel() %}
        Appier - {{ owner.description }}
    {% else %}
        {{ owner.description }}
    {% endif %}
{% endblock %}
{% block content %}
    <div class="message">
        <div class="header">
            {% if own.is_devel() %}
                <h1>Welcome to Appier Framework</h1>
                <p>You've just configured <strong>{{ owner.description }}</strong> correctly, now it's time to start the development.</p>
                <p>Please be aware that you're currently running <a href="http://appier.hive.pt" target="_blank">Appier</a> in development mode, to change that increase the logging level.</p>
            {% else %}
                {% if own.observations %}
                    <h1>{{ owner.description }}</h1>
                    <p>{{ owner.observations }}.</p>
                {% else %}
                    <h1 class="single">{{ owner.description }}</h1>
                {% endif %}
            {% endif %}
        </div>
    </div>
{% endblock %}
