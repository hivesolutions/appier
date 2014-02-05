{% extends "layout.html.tpl" %}
{% block title %}
    Appier - Error
{% endblock %}
{% block content %}
    <div class="debugger">
        <div class="header">
            <h1>{{ full_name }}</h1>
            <p>{{ code }} - {{ message }}</p>
        </div>
        <div class="traceback">
            {% for line in lines %}
                <div class="line">{{ line }}</div>
            {% endfor %}
        </div>
    </div>
{% endblock %}
