{% extends "partials/layout.static.html.tpl" %}
{% block title %}Table{% endblock %}
{% block name %}Table{% endblock %}
{% block content %}
    <table class="table table-list">
        <thead>
            <tr>
                <th class="left label" width="16%">Date</th>
                <th class="left label" width="70%">Description</th>
                <th class="right label" width="14%">Variation</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="left">2010/06/07</td>
                <td class="left"><a href="#">First Item</a></td>
                <td class="right">down</td>
            </tr>
            <tr>
                <td class="left">2010/06/06</td>
                <td class="left"><a href="#">Second Item</a></td>
                <td class="right">up</td>
            </tr>
            <tr>
                 <td class="left">2010/06/05</td>
                <td class="left"><a href="#">Third Item</a></td>
                <td class="right">down</td>
            </tr>
            <tr>
                  <td class="left">2010/06/04</td>
                <td class="left"><a href="#">Fourth Item</a></td>
                <td class="right">up</td>
            </tr>
        </tbody>
    </table>
{% endblock %}
