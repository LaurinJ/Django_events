$(document).ready(() => {
    setup_carousel();

    if (window.location.pathname.match('/.*register.*/')) {

        $("#id_username").change(() => {
            check_field_value_exists(
                form_cls='register-form',
                field_identifier="#id_username",
                validation_attr='data-validation'
            );
        });

        $("#id_email").change(() => {
            check_field_value_exists(
                form_cls='register-form',
                field_identifier="#id_email",
                validation_attr='data-validation'
            );
        });
    }
});


function setup_carousel() {
    $('.owl-carousel').owlCarousel({
            loop:true,
            margin:10,
            nav:true,
            dots:false,
            autoHeight:true,
            autoWidth: true,
        });
}

function check_field_value_exists(form_cls, field_identifier, validation_attr){
    let form = document.getElementById(form_cls);
    let field = $(field_identifier);

    let err = field.next('.error');
    if (err) {err.remove()};

    $.ajax({
        url: form.getAttribute(validation_attr),
        data: {
            'field_name': field_identifier.replace('#id_', ''),
            'field_value': field.val(),
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val(),
        },
        type: "POST",
        dataType: 'json',

        success: (json) => {
            if (json.exists) {
                field.after(`<span   class='error'>${json.error_message}</span>`);
            }
        },

        error: (jqXHR, err_desc, exc_obj) => {
            console.log(exc_obj);
        },

    });
}