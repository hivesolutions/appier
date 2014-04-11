{% extends "partials/layout.fluid.html.tpl" %}
{% block title %}Form{% endblock %}
{% block name %}Form{% endblock %}
{% block content %}
    <form action="{{ url_for('form') }}" enctype="multipart/form-data" method="post" class="form inline">
        <div class="section">
            <div class="item">
                <div class="label">
                    <label>Username</label>
                </div>
                <div class="input">
                    <input type="text" class="text-field" name="username" placeholder="eg: joamag"
                           value="root" data-disabled="1" data-error="" />
                </div>
            </div>
            <div class="item">
                <div class="label">
                    <label>First Name</label>
                </div>
                <div class="input">
                    <input type="text" class="text-field" name="first_name" value="Super"
                           data-error="" />
                </div>
            </div>
            <div class="item">
                <div class="label">
                    <label>Last Name</label>
                </div>
                <div class="input">
                    <input type="text" class="text-field" name="last_name" value="Administrator"
                           data-error="" />
                </div>
            </div>
            <div class="item">
                <div class="label">
                    <label>Password</label>
                </div>
                <div class="input">
                    <input type="password" class="text-field" name="password"
                           value="" data-error="" />
                </div>
            </div>
            <div class="item">
                <div class="label">
                    <label>Confirmation</label>
                </div>
                <div class="input">
                    <input type="password" class="text-field" name="password_confirm"
                               value="" data-error="" />
                </div>
               </div>
           </div>
        <div class="separator strong"></div>
        <div class="section">
            <div class="item clear">
                <div class="label">
                    <label>Birthday</label>
                </div>
                <div class="input">
                    <input type="text" name="birthday" class="text-field" data-type="date"
                           placeholder="yyyy/mm/dd" value="" data-error="" />
                </div>
            </div>
            <div class="item">
                <div class="label">
                    <label>Gender</label>
                </div>
                <div class="input">
                    <input type="radio" name="gender" id="male" value="male" checked="1" />
                    <label class="radio-label" for="male">Male</label>
                    <input type="radio" name="gender" id="female" value="female" />
                    <label class="radio-label" for="female">Female</label>
                </div>
            </div>
        </div>
        <div class="separator strong"></div>
        <div class="item">
            <div class="label">
                <label>Phone</label>
            </div>
            <div class="input">
                <input type="text" class="text-field" name="phone" value="+351999999999"
                       data-disabled="1" data-error="" />
            </div>
        </div>
        <div class="item">
            <div class="label">
                <label>Email</label>
            </div>
            <div class="input">
                <input type="email" class="text-field" name="email" value="root@root.com"
                       data-disabled="1" data-error="" />
            </div>
        </div>
        <div class="item">
            <div class="label">
                <label>Address</label>
            </div>
            <div class="input">
                <input type="text" class="text-field street" name="street" placeholder="street name"
                       value="" data-error="" />
                <span class="multiline">
                    <input type="text" class="text-field zip-code" name="zip_code" placeholder="zip code"
                           value="" data-error="" />
                    <input type="text" class="text-field province" name="province" placeholder="province"
                           value="" data-error="" />
                </span>
                <div name="country" class="drop-field drop-field-select" value="Portugal"
                     data-name="country" data-error=""
                     data-number_options="-1">
                    <div class="data-source" data-type="countries"></div>
                </div>
            </div>
        </div>
        <div class="separator strong"></div>
        <div class="item full">
            <div class="label">
                <label>About</label>
            </div>
            <div class="input">
                 <textarea name="about" class="text-area" placeholder="eg: some words about yourself"
                           data-error=""></textarea>
            </div>
        </div>
        <div class="item full">
            <div class="label">
                <label>Image (200x200)</label>
            </div>
            <div class="input">
                 <a data-name="image" class="uploader" data-error="">Select & Upload the image file</a>
            </div>
        </div>
        <div class="separator strong"></div>
        <div class="buttons">
            <span class="button button-color button-green" data-submit="true">Update</span>
            <span class="or">or</span>
            <span class="button button-color button-grey" data-link="{{ url_for('show') }}">Cancel</span>
        </div>
    </form>
{% endblock %}
