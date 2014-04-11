{% extends "partials/layout.static.html.tpl" %}
{% block title %}Show{% endblock %}
{% block name %}Show{% endblock %}
{% block content %}
    <div class="quote">Name</div>
    <div class="separator-horizontal"></div>
    <table>
        <tbody>
            <tr>
                <td class="right label" width="50%">place</td>
                <td class="left value" width="50%">Place</td>
            </tr>
            <tr>
                <td class="right label" width="50%">country</td>
                <td class="left value" width="50%">Country</td>
            </tr>
            <tr>
                <td class="right label" width="50%">description</td>
                <td class="left value" width="50%">Description</td>
            </tr>
        </tbody>
    </table>
{% endblock %}
