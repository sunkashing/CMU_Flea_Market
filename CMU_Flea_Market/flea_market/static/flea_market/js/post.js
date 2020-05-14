$(document).ready(function () {
    $('#file-button').click(function () {
        $('#id_product_picture').trigger('click');
    });

});

function previewFile() {
    let preview = document.querySelector('img[id=preview-image]');
    let file    = document.querySelector('input[type=file]').files[0];
    let reader  = new FileReader();

    reader.onloadend = function () {
        preview.src = reader.result;
    };

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
    }
}

function previewName() {
    let name = $('#id_product_name').val();
    $('#item-name').html(name);
}

function previewPrice() {
    let price = $('#id_product_price').val();
    $('#item-price').html('$' + price);
}

function previewCategory() {
    let category = $('#id_product_category').val();
    $('#item-category').html(CAT[category]);
}

function previewDescription() {
    let description = $('#id_product_description').val().replace(/\n/g, '<br>');
    $('#item-description').html(description);
}

function previewStatus() {
    let statusNum = $('#id_product_status').val();
    if (statusNum <= 1) {
        $('#item-status').html("(fair)");
    } else if (statusNum <= 2) {
        $('#item-status').html("(good)");
    } else if (statusNum <= 3) {
        $('#item-status').html("(very good)");
    } else if (statusNum <= 4) {
        $('#item-status').html("(excellent)");
    } else {
        $('#item-status').html("(brand new)");
    }
}

let CAT = {'Clothes': 'person',
    'Electronic Devices': 'power',
    'Cars': 'drive_eta',
    'House Leasing': 'house',
    'Books': 'menu_book'};
