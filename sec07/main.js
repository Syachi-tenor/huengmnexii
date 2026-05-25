async function get_token(username, password) {
    const details = new URLSearchParams();
    details.append('username', username);
    details.append('password', password);
    details.append('grant_type', 'password');
    const response = await fetch('/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: details.toString(),
    });
    if (!response.ok) throw new Error('Auth failed');
    const data = await response.json();
    console.log('Access Token:', data.access_token);
    localStorage.setItem('token', data.access_token);
}

async function logout() {
    localStorage.removeItem('token')
    window.location.href = '/'
}

async function get_username() {
    let url = server + '/users/me/'
    return await api_request_get(url)
}

$(function () {
    const token = localStorage.getItem('token');
    $('#login').hide()
    $('#main').hide()
    if(token){
        $('#main').show()
        // 一旦 Messages を取得，あとは interval 毎取得
        message_get_all()
        if (interval_id !== null) {
            clearInterval(interval_id)
        }
        interval_id = setInterval(message_get_all, interval)
        get_username().then(value => {
            console.log(value['username'])
            $('#post_message_name_display').append(' ' + value['username'])
        })
    } else {
        $('#login').show()
    }
    $('button#login_button').on(
        'click', function () {
            $('#login_message').empty()
            let username = $('#login_username').val().trim()
            let password = $('#login_password').val().trim()
            get_token(username, password).then(value => {
                window.location.href = '/'
            }).catch((error) => {
                $('#login_message').append('Login Error')
            })
        })
    $('button#sign_up_button').on(
        'click', function () {
            $('#login_message').empty()
            let username = $('#login_username').val().trim()
            let password = $('#login_password').val().trim()
            let data = {
                username: username,
                password: password
            }
            let url = '/users'
            api_request_post(url, data).then(value => {
                if (value != 'Success') {
                    $('#login_message').append(value)
                } else {
                    get_token(username, password).then(value => {
                        window.location.href = '/'
                    }).catch((error) => {
                        $('#login_message').append('Login Error')
                    })
                }
            }).catch((error) => {
                $('#login_message').append('Sign Up Error')
            })
        })
    $('button#logout_button').on(
        'click', function () {
            logout()
        })
})
