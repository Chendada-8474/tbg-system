$(document).ready(function () {




    $("#carBrand").on('change', function () {

        var brand = new Object()
        brand["brand"] = $(this).val()


        $("select#vehicle > option").each(function () {
            $(this).remove()
        })

        $.ajax({
            method: "post",
            url: "/live-car",
            dataType: "json",
            data: JSON.stringify(brand),
            success: function (res) {
                res['cars'].forEach(element => {
                    $('select#vehicle').append(`<option value='${element[0]}'>${element[1]}</option>`)
                });
            }
        })
    })




})