
$(document).ready(function() {
    let card = $(".card");

    let a = $('.card-link');
    a.click(function (event) {
        let event_id = event.target.id;
        if (event.target.id.includes('item-follow-button-') || event_id.includes('item-follow-')) {
            return false;
        }
    });

    let follow_button = $('.item-follow');
    follow_button.click(function () {
        let hidden_item_id = $(this).siblings('.hidden-item-id').val();
        $.ajax({
            url: "/flea_market/follow_action?item_id=" + hidden_item_id,
            dataType : "json",
            success: update
        });
    })

});


function update(response) {
    let item_id = response.item_id
    let follow_status = response.follow_status
    item_a_tag = 'item-follow-' + item_id;
    item_b_tag = 'item-follow-button-' + item_id;
    let item = $('#' + item_a_tag);
    let item_button = $('#' + item_b_tag);
    if (follow_status === 'true') {
        item.text('favorite');
        item_button.css({'transform': 'translateY(-30px)', 'transition': 'transform 1s'})
    } else {
        item.text('favorite_border');
        item_button.css({'transform': 'translateY(0)', 'transition': 'transform 1s'})
    }

}

