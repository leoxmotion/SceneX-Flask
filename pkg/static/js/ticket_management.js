$(function() {
    var ticketFormContainer = $('#ticketFormContainer');
    var ticketForm = $('#ticketForm');
    var ticketCategory = $('#ticketCategory');
    var ticketPrice = $('#ticketPrice');
    var seatsPerTicketGroup = $('#seatsPerTicketGroup');
    var seatsPerTicketLabel = $('#seatsPerTicketLabel');
    var saveTicketBtn = $('#saveTicketBtn');
    var cancelTicketEditBtn = $('#cancelTicketEditBtn');
    var ticketCardsWrapper = $('#ticketCardsWrapper');
    var addTicketButton = $('.toggle-ticket-form-btn');
    var currentTicketId = null;

    function updateFormVisibility() {
        ticketFormContainer.slideDown(300);
    }

    function resetForm() {
        ticketForm[0].reset();
        ticketForm.find('input[name="ticket_id"]').val('');
        currentTicketId = null;
        saveTicketBtn.text('Add Ticket');
        cancelTicketEditBtn.hide();
        setCategoryFields(ticketCategory.val());
    }

    function setCategoryFields(category) {
        if (category === 'free') {
            ticketPrice.val(0);
            $('#priceField').hide();
            seatsPerTicketGroup.hide();
        } else if (category === 'paid') {
            $('#priceField').show();
            seatsPerTicketGroup.hide();
            seatsPerTicketLabel.text('Seats Per Ticket');
        } else if (category === 'table') {
            $('#priceField').show();
            seatsPerTicketGroup.show();
            seatsPerTicketLabel.text('Seats Per Table');
        }
    }

    addTicketButton.click(function() {
        if (ticketFormContainer.is(':visible')) {
            ticketFormContainer.slideUp(300);
        } else {
            ticketFormContainer.slideDown(300);
        }
    });

    ticketCategory.change(function() {
        setCategoryFields($(this).val());
    });

    cancelTicketEditBtn.click(function() {
        resetForm();
        ticketFormContainer.slideUp(300);
    });

    function renderTicketCard(ticket) {
        var priceText = ticket.price === 0 ? 'Free' : '₦' + ticket.price.toLocaleString();
        var salesStart = ticket.sales_start || 'Not set';
        var salesEnd = ticket.sales_end || 'Not set';
        var seatsHtml = ticket.category === 'table' ?
            '<div class="ticket-card-row"><span>Seats Per Table</span><strong>' + ticket.seats_per_ticket + '</strong></div>' : '';
        var activeClass = ticket.active ? 'active' : 'inactive';

        return '<div class="ticket-card" data-ticket-id="' + ticket.id + '">' +
            '<div class="ticket-card-header"><div><h4>' + ticket.name + '</h4><span class="ticket-category badge badge-secondary">' + ticket.category.charAt(0).toUpperCase() + ticket.category.slice(1) + '</span></div><div class="ticket-card-status ' + activeClass + '">' + (ticket.active ? 'Active' : 'Inactive') + '</div></div>' +
            '<div class="ticket-card-body">' +
            '<div class="ticket-card-row"><span>Price</span><strong>' + priceText + '</strong></div>' +
            '<div class="ticket-card-row"><span>Available Quantity</span><strong>' + ticket.quantity + '</strong></div>' +
            '<div class="ticket-card-row"><span>Sold</span><strong>' + ticket.sold + '</strong></div>' +
            '<div class="ticket-card-row"><span>Maximum Per Order</span><strong>' + ticket.max_per_order + '</strong></div>' +
            seatsHtml +
            '<div class="ticket-card-row"><span>Sales Start</span><strong>' + salesStart + '</strong></div>' +
            '<div class="ticket-card-row"><span>Sales End</span><strong>' + salesEnd + '</strong></div>' +
            '<div class="ticket-card-row ticket-card-description"><span>Description</span><p>' + (ticket.description || 'No description provided.') + '</p></div>' +
            '</div>' +
            '<div class="ticket-card-actions"><button class="btn btn-outline-primary btn-sm edit-ticket-btn" data-ticket-id="' + ticket.id + '">Edit</button><button class="btn btn-outline-danger btn-sm delete-ticket-btn" data-ticket-id="' + ticket.id + '">Delete</button></div>' +
            '</div>';
    }

    function attachCardEvents(card) {
        card.find('.edit-ticket-btn').click(function() {
            var ticketCard = card;
            var ticketId = ticketCard.data('ticket-id');
            var ticket = {
                id: ticketId,
                name: ticketCard.data('ticket-name'),
                category: ticketCard.data('ticket-category'),
                description: ticketCard.data('ticket-description'),
                price: parseFloat(ticketCard.data('ticket-price')) || 0,
                quantity: parseInt(ticketCard.data('ticket-quantity'), 10) || 0,
                max_per_order: parseInt(ticketCard.data('ticket-max-per-order'), 10) || 0,
                seats_per_ticket: parseInt(ticketCard.data('ticket-seats-per-ticket'), 10) || 0,
                sales_start: ticketCard.data('ticket-sales-start') || '',
                sales_end: ticketCard.data('ticket-sales-end') || '',
            };

            ticketForm.find('input[name="ticket_id"]').val(ticket.id);
            ticketForm.find('input[name="name"]').val(ticket.name);
            ticketForm.find('select[name="category"]').val(ticket.category);
            ticketForm.find('textarea[name="description"]').val(ticket.description);
            ticketForm.find('input[name="price"]').val(ticket.price);
            ticketForm.find('input[name="quantity"]').val(ticket.quantity);
            ticketForm.find('input[name="max_per_order"]').val(ticket.max_per_order);
            ticketForm.find('input[name="seats_per_ticket"]').val(ticket.seats_per_ticket);
            ticketForm.find('input[name="sales_start"]').val(ticket.sales_start);
            ticketForm.find('input[name="sales_end"]').val(ticket.sales_end);

            saveTicketBtn.text('Update Ticket');
            cancelTicketEditBtn.show();
            setCategoryFields(ticket.category);
            updateFormVisibility();
        });

        card.find('.delete-ticket-btn').click(function() {
            var ticketId = $(this).data('ticket-id');
            if (!confirm('Are you sure you want to delete this ticket?')) {
                return;
            }

            $.ajax({
                url: '/creator/tickets/' + ticketId + '/delete',
                type: 'POST',
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        $('.ticket-card[data-ticket-id="' + ticketId + '"]').fadeOut(300, function() {
                            $(this).remove();
                            if ($('#ticketCardsWrapper').children('.ticket-card').length === 0) {
                                $('#ticketCardsWrapper').html('<div class="empty-state"><h4>No tickets have been created for this event yet.</h4><p>Click "Add Tickets" to create your first ticket.</p></div>');
                            }
                        });
                    }
                }
            });
        });
    }

    ticketCardsWrapper.children('.ticket-card').each(function() {
        attachCardEvents($(this));
    });

    ticketForm.submit(function(event) {
        event.preventDefault();

        var eventId = window.location.pathname.split('/')[3];
        var ticketId = ticketForm.find('input[name="ticket_id"]').val();
        var url = ticketId ? '/creator/tickets/' + ticketId + '/update' : '/creator/events/' + eventId + '/tickets/add';
        var requestData = ticketForm.serialize();

        $.ajax({
            url: url,
            type: 'POST',
            data: requestData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var cardHtml = renderTicketCard(response.ticket);
                    if (ticketId) {
                        var existingCard = $('.ticket-card[data-ticket-id="' + ticketId + '"]');
                        existingCard.replaceWith(cardHtml);
                    } else {
                        if ($('#ticketCardsWrapper').find('.empty-state').length) {
                            $('#ticketCardsWrapper').empty();
                        }
                        $('#ticketCardsWrapper').append(cardHtml);
                    }
                    resetForm();
                    ticketFormContainer.slideUp(300);
                    attachCardEvents($('.ticket-card[data-ticket-id="' + response.ticket.id + '"]'));
                } else {
                    alert(response.error || 'Unable to save ticket.');
                }
            },
            error: function() {
                alert('An error occurred while saving the ticket.');
            }
        });
    });

    setCategoryFields(ticketCategory.val());
});
