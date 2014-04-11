{% include "partials/doctype.html.tpl" %}
<head>
    {% block head %}
        {% include "partials/content_type.html.tpl" %}
        {% include "partials/includes.html.tpl" %}
        <title>Layout / {% block title %}{% endblock %}</title>
    {% endblock %}
</head>
<body class="ux wait-load fluid grey no-footer {{ session.sub_type }} {{ session.style }}" >
    {% block extras %}
        {% include "partials/extras.html.tpl" %}
    {% endblock %}
    <div id="overlay" class="overlay"></div>
    <div id="bar" class="bar">
        {% include "partials/bar.html.tpl" %}
    </div>
    <div id="header" class="header">
        {% include "partials/header.html.tpl" %}
        {% block header %}
            <div class="side-links">
                {% for model in models %}
                    <a href="#">{{ model._name() }}</a>
                {% endfor %}
            </div>
        {% endblock %}
    </div>
    <div id="content" class="content {% block style %}{% endblock %}">
        <div class="content-header">
            <h1>{% block name %}{% endblock %}</h1>
            <div class="content-buttons">
                {% block buttons %}{% endblock %}
            </div>
        </div>
        <div class="content-container">
            {% block content %}{% endblock %}
        </div>
    </div>
    <div id="footer" class="footer">
        {% include "partials/footer.html.tpl" %}
        {% block footer %}{% endblock %}
    </div>
</body>
{% include "partials/end_doctype.html.tpl" %}
