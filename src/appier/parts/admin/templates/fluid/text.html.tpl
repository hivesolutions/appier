{% extends "partials/layout.fluid.html.tpl" %}
{% block title %}Text{% endblock %}
{% block name %}Text{% endblock %}
{% block buttons %}
    {{ super() }}
    <div class="button button-color button-grey" data-link="/accounts/own/edit">Edit</div>
{% endblock %}
{% block extras %}
    <div class="side-panel border-box">
        <form class="form">
            <h1>Get news updates</h1>
            <input type="text" class="text-field" placeholder="Your email address"
                   data-object="textfield" autocomplete="off" data-value="" />
            <div class="buttons">
                <div class="button button-color button-green button-confirm" data-submit="1">Sign Up</div>
                <div class="button button-color button-grey button-cancel">Cancel</div>
            </div>
        </form>
    </div>
{% endblock %}
{% block content %}
    <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce tristique viverra libero, quis euismod neque feugiat nec. Ut laoreet hendrerit sem at dapibus.
        Donec rutrum nibh id pellentesque luctus. Sed enim est, molestie vel ipsum eu, gravida sagittis metus. Cras cursus eros erat, sed pharetra nisi rhoncus vel.
        Aliquam pulvinar lorem in dui placerat, ac pretium eros eleifend. Aenean id imperdiet quam. Ut in justo quam. Sed rhoncus tortor ac sapien lobortis vestibulum.
        Suspendisse scelerisque leo id ipsum laoreet, eget euismod diam gravida.
    </p>
    <p>
        Nulla mattis eget odio eu volutpat. Morbi porttitor mauris auctor augue malesuada molestie. Nulla aliquam vitae risus sed dapibus. Maecenas et nisi tristique,
        ultrices mauris sit amet, convallis dolor. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed tempor dui at lectus
        lobortis adipiscing. Cras egestas cursus tellus.
    </p>
    <p>
        Aliquam at ante augue. Vivamus augue odio, auctor non urna a, mollis ornare velit. Donec a elit pharetra, imperdiet magna id, laoreet purus. Curabitur tincidunt
        a eros et dictum. Cras fringilla non odio et auctor. Phasellus quis aliquet ligula, in luctus libero. Donec ipsum ipsum, pharetra vel turpis et, facilisis convallis
        justo. Duis ac nisi malesuada, rutrum erat nec, faucibus magna. Proin lobortis orci quis sodales accumsan. Phasellus id tincidunt metus. Aliquam a semper neque.
        Fusce urna sapien, rutrum et ultricies sit amet, molestie nec felis. Nunc sagittis nibh id odio euismod fringilla. Phasellus libero ligula, pellentesque at bibendum
        non, accumsan sit amet enim. Aenean luctus lobortis mollis.
    </p>
    <p>
        Mauris sodales nulla neque, fermentum tempor lectus tempus rhoncus. Sed sed ipsum felis. Vivamus fringilla quis enim ac ornare. Nam vitae purus ac nunc sodales
        consectetur nec at arcu. Praesent fringilla sem sem, a sodales odio placerat ut. Quisque et risus non arcu euismod sodales id non neque. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed bibendum nibh vitae sagittis imperdiet. Morbi quis libero eu ante pellentesque bibendum.
    </p>
    <p>
        Quisque bibendum luctus vehicula. Suspendisse imperdiet nibh ac sapien mollis laoreet. Aenean fringilla lacus a cursus elementum. Nullam eu vestibulum nibh.
        Nulla facilisi. Sed metus metus, fringilla eget est quis, ullamcorper porttitor lacus. Pellentesque elementum, lorem in pulvinar rutrum, lacus leo vestibulum enim,
        at semper magna elit id eros. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In fermentum, tellus ac ultricies pellentesque, diam mauris dictum justo,
        vel blandit massa felis nec orci. Vestibulum consectetur, nulla quis rhoncus placerat, urna metus pretium purus, ultricies faucibus dui massa in massa.
    </p>
{% endblock %}
