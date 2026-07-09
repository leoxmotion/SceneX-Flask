$(document).ready(function(){

$(document).on('click', '.comment-btn', function () {

    window.location.href = $(this).data('url');

});

$(document).on('click', '.view-event-btn', function () {

    window.location.href = $(this).data('url');

});

// ==========================
// Event Buttons
// ==========================

$(document).on('click', '.edit-event-btn', function () {

    window.location.href = $(this).data('url');

});

$(document).on('click', '#editProfileBtn', function () {

    window.location.href = $(this).data('url');

});

$(document).on('click', '.add-ticket-btn', function () {

    window.location.href = $(this).data('url');

});

$(document).on('click', '.delete-event-btn', function () {

    window.location.href = $(this).data('url');

});

$(document).on('click', '.toggle-ticket-form-btn', function () {

    $('#ticketFormContainer').slideToggle(250);

    $(this).find('i').toggleClass('fa-ticket fa-xmark');

    if ($(this).find('i').hasClass('fa-xmark')) {
        $(this).contents().last()[0].textContent = ' Close';
    } else {
        $(this).contents().last()[0].textContent = ' Add Ticket';
    }

});

$(document).on("click", ".viewBtn", function () {
    let eventId = $(this).data("view-event");
    window.location.href = "/creator/view-event/" + eventId + "/";
});

$(document).on("click", "#createCommBtn", function () {
    window.location.href = "/create_community/";
});

$(document).on("click", ".ed-rsvp-btn", function () {
    window.location.href = "/rsvp/";
});

$(document).on("click", ".viewCommBtn", function () {
    const commId = $(this).data("comm-id");
    window.location.href = "/comm_detail/" + commId + "/";
});

});

