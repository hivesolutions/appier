<div class="top-bar">
    <div class="container">
        <div class="logo">
            <a>layout.css</a>
        </div>
        <div class="drop-field entities" placeholder="Search over some of the items"
             data-number_options="4">
            <li class="template">
                <img class="picture" data-src="{{ url_for('static', filename = 'images/avatar_64.png') }}" />
                <div>
                    <p class="title">%[name]</p>
                    <p class="description">%[details]</p>
                </div>
            </li>
            <ul class="data-source" data-type="local">
                <li>
                    <span name="name">User 1</span>
                    <span name="details">user1@hive.pt</span>
                </li>
                <li>
                    <span name="name">User 2</span>
                    <span name="details">user2@hive.pt</span>
                </li>
                <li>
                    <span name="name">User 3</span>
                    <span name="details">user3@hive.pt</span>
                </li>
                <li>
                    <span name="name">User 4</span>
                    <span name="details">user4@hive.pt</span>
                </li>
                <li>
                    <span name="name">User 5</span>
                    <span name="details">user5@hive.pt</span>
                </li>
                <li>
                    <span name="name">User 6</span>
                    <span name="details">user6@hive.pt</span>
                </li>
            </ul>
        </div>
        <div class="right">
            <div class="menu system-menu">
                <div class="menu-button">
                    <a class="menu-link" data-no_left="1">User</a>
                </div>
                <div class="menu-contents">
                    <div class="header-contents">
                        <img class="avatar-image" src="{{ url_for('static', filename = 'images/avatar_64.png') }}" />
                        <div class="avatar-contents">
                            <h2>User</h2>
                            <h3>user@hive.pt</h3>
                        </div>
                    </div>
                    <div class="footer-contents">
                        <a href="#">Logout</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
