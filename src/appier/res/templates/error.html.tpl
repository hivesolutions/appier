{% extends "layout.html.tpl" %}
{% block title %}
    Appier - Error
{% endblock %}
{% block head %}
    {{ super() }}
    {% set highlighter = config.conf("HIGHLIGHTER", "prism") %}
    {% if highlighter == "prism" %}
        <link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/prism/1.6.0/themes/prism.min.css" />
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/prism/1.6.0/prism.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/prism/1.6.0/components/prism-python.min.js"></script>
    {% endif %}
    {% if highlighter == "highlight.js" %}
        <link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/github.min.css" />
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>
    {% endif %}
{% endblock %}
{% block content %}
    <div class="debugger">
        <div class="header">
            <h1>{{ full_name }}</h1>
            <p>{{ code }} - {{ message }}</p>
        </div>
        {% if lines %}
            <div class="traceback">
                {% if extended %}
                    {% for item in extended %}
                        <div class="line">File "{{ item.path }}", line {{ item.lineno }}, in {{ item.context }}
                            {% if item.git_url %}
                                &bull; <a class="image" href="{{ item.git_url }}" target="_blank">{{ item.git_service|default("git", True) }}</a>
                            {% endif %}
                        </div>
                        <a class="line opener" data-id="{{ item.id }}">{{ item.line }}</a>
                        <div class="lines-extra" data-id="{{ item.id }}" data-start="{{ item.start }}" data-end="{{ item.end }}">
                            {% for line in item.lines %}
                                <div class="line {% if line.is_target %}target{% endif %}">
                                    <span class="lineno">{{ line.lineno }}</span><span class="text">{{ line.line|nl_to_br|sp_to_nbsp }}</span>
                                </div>
                            {% endfor %}
                            {% if item.contents %}
                                <div class="raw" >{{ item.contents_d }}</div>
                            {% endif %}
                        </div>
                    {% endfor %}
                {% else %}
                    {% for line in lines %}
                        <div class="line">{{ line }}</div>
                    {% endfor %}
                {% endif %}
            </div>
        {% endif %}
    </div>
{% endblock %}
{% block footer %}
    {{ super() }}
    <br/>{{ uid }}
{% endblock %}
