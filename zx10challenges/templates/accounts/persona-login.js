navigator.id.watch({
    {% if current_user.is_authenticated() %}
    loggedInUser: {{ current_user.email|tojson|safe }},
    {% else %}
    loggedInUser: null,
    {% endif %}

    onlogin: function (assertion) {
        $.ajax({
            type: 'POST',
            url: {{ url_for('accounts.persona_login')|tojson|safe }},
            data: {assertion: assertion},

            success: function (res, status, xhr) {
                window.location.reload();
            },

            error: function (res, status, xhr) {
                navigator.id.logout();
                alert("Logging you in failed: " + status);
            },
        });
    },

    onlogout: function () {
        $.ajax({
            type: 'POST',
            url: {{ url_for('accounts.persona_logout')|tojson|safe }},

            success: function (res, status, xhr) {
                window.location.reload();
            },

            error: function (res, status, xhr) {
                alert("Logging you out failed: " + status);
            },
        });
    }
});


$(document).on('click', '.persona-login-button', function (e) {
    e.preventDefault();
    navigator.id.request();
});


$(document).on('click', '.persona-logout-button', function (e) {
    e.preventDefault();
    navigator.id.logout();
});

