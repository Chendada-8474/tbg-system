$(document).ready(function () {

    $('#item_class').on('change', function () {


        var item_class_id = new Object()

        item_class_id["item_class"] = $(this).val()
        $("select#itemId > option").each(function () {
            $(this).remove()
        })

        $.ajax({
            method: "post",
            url: "/live-item-class",
            dataType: "json",
            data: JSON.stringify(item_class_id),
            success: function (res) {
                console.log(res)
                res['item_class'].forEach(element => {
                    $('select#itemId').append(`<option value='${element[0]}'>${element[1]}</option>`)
                });
            }
        })

    })

})