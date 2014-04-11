{% extends "partials/layout.fluid.html.tpl" %}
{% block title %}Table{% endblock %}
{% block name %}Table{% endblock %}
{% block style %}no-header no-padding{% endblock %}
{% block content %}
    <div class="filter" data-no_input="1">
        <table>
            <thead>
                <tr class="table-row table-header">
                    <th class="text-left" data-width="190">Sender</th>
                    <th class="text-left">Subject</th>
                    <th class="text-right" data-width="190">Last Login</th>
                </tr>
            </thead>
            <tbody class="filter-contents">
                <tr class="table-row">
                    <td class="text-left">
                        <a href="#">João Magalhães</a>
                    </td>
                    <td class="text-left">Próximos eventos música @ FNAC</td>
                    <td class="text-right timestamp" data-width="190">Porto</td>
                </tr>
                <tr class="table-row">
                    <td class="text-left">
                        <a href="#">Gondomar</a>
                    </td>
                    <td class="text-left">Coisas pendentes para o oibiquini</td>
                    <td class="text-right timestamp" data-width="190">Porto</td>
                </tr>
                <tr class="table-row">
                    <td class="text-left">
                        <a href="#">Gondomar</a>
                    </td>
                    <td class="text-left">Próximos eventos música @ FNAC</td>
                    <td class="text-right timestamp" data-width="190">Porto</td>
                </tr>
                <tr class="table-row">
                    <td class="text-left">
                        <a href="#">António Gouveia</a>
                    </td>
                    <td class="text-left">[Omni API] implementar o wrap_exception flag</td>
                    <td class="text-right timestamp" data-width="190">Porto</td>
                </tr>
            </tbody>
        </table>
        <div class="filter-no-results quote">
            No results found
        </div>
        <div class="filter-more">
            <span class="button more">Load more</span>
            <span class="button load">Loading</span>
        </div>
    </div>
{% endblock %}
