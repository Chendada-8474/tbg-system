$(function () {
    $("#days").sortable();
    $(".schedule").sortable();
});

// add input day
const divItinerary = document.getElementById("days")
const numDay = divItinerary.childElementCount
const numSchedule = document.getElementsByClassName("one-schedule").length
var dayCount = numDay + 1
var scheduleCount = numSchedule + 1


//  reset the orderation od days


function reactive_all_handler() {
    active_spot_change()
    active_accommodation_change()
    active_add_day_click()
    active_add_schedule()
    active_delete_day()
    active_delete_schedule()
    reorder_click()
}


function reorder_click() {
    $('#reorder').off('click')
    $('#reorder').click(function () {


        first_day = 0
        first_schedule = 1
        $("#days").find("h4").each(function () {
            $(this).text(`Day ${first_day}`)
            first_day += 1
            dayIdReorder = $(this).parent().attr("id")
            $(`#${dayIdReorder}`).find("div.schedule-header").each(function () {
                $(this).text(`#${first_schedule}`)
                first_schedule += 1
            })
            first_schedule = 1
        })
    })
}

// live spot ajax
function active_spot_change() {
    $(".filter").off()
    $(".filter").on('change', function () {
        dayIdLive = $(this).parent().parent().attr('id');

        $(`#${dayIdLive}`).find("select.spot > option").each(function () {
            $(this).remove()
        })
        var filter = new Object();
        $(`#${dayIdLive}`).find('div.card-body > select.filter').each(function (index) {
            filter[this.name] = $(this).val();
        })
        $.ajax({
            method: "post",
            url: "/live-spot",
            dataType: "json",
            data: JSON.stringify(filter),
            success: function (res) {
                res.forEach(element => {
                    $(`#${dayIdLive}`).find('select.spot').append(`<option value='${element[0]}'>${element[1]}</option>`)
                });
            }
        })
    })
}

function active_accommodation_change() {
    $('.filter_accommodation').off()
    $('.filter_accommodation').on('change', function () {
        dayIdLive = $(this).parent().parent().parent().attr('id');
        $(`#${dayIdLive}`).find("select.accommodation > option").each(function () {
            $(this).remove()
        })
        filter_accommodation = $(`#${dayIdLive}`).find('select.filter_accommodation').val()

        $.ajax({
            method: "post",
            url: "/live-accommodation",
            dataType: "json",
            data: JSON.stringify(filter_accommodation),
            success: function (res) {
                res.forEach(element => {
                    $(`#${dayIdLive}`).find('select.accommodation').append(`<option value='${element[0]}'>${element[1]}</option>`)
                });
            }
        })

    })
}

function active_add_day_click() {
    $('#add-day').off('click')
    $('#add-day').click(function () {

        newDay = $('#day1').clone().attr("id", `day${dayCount}`)
        newDay.find('div.one-schedule[id!="schedule1"]').each(function () {
            $(this).remove()
        })
        newDay.find("#schedule1").attr('id', `schedule${scheduleCount}`)
        newDay.find('h4').text('New Day')
        newDay.find('div.schedule-header').text('New Spot')
        newDay.find('button.delete-day').removeAttr('disabled')
        newDay.find('input[name="number_of_schedule"]').attr('value', 1)
        newDay.find('select.accommodation').find('option').each(function () {
            $(this).remove()
        })
        newDay.find('select.accommodation').append('<option value=15>-- TBA --</option>')



        $('#days').append(newDay)

        dayCount += 1
        scheduleCount += 1
        active_spot_change()
        active_accommodation_change()
        active_add_schedule()
        active_delete_schedule()
        active_delete_day()
        reorder_click()
        $(".schedule").sortable();
    })
}



function active_add_schedule() {
    $(".add-schedule").off('click')
    $(".add-schedule").click(function () {

        dayId = $(this).parent().parent().attr('id')
        newCard = $("#schedule1").clone().attr("id", `schedule${scheduleCount}`)

        newCard.find("div.schedule-header").text("New Spot")
        newCard.find('button.delete-schedule').removeAttr('disabled')
        scheduleCount += 1

        $(`#${dayId}`).find("div.schedule").append(newCard)

        update_number_schedule(dayId, "addition")

        active_spot_change()
        active_add_day_click()
        active_delete_schedule()
        reorder_click()
    })
}

function active_delete_schedule() {
    $('button.delete-schedule').off('click')
    $('button.delete-schedule').click(function () {
        scheduleIdDelete = $(this).parent().parent().attr('id')
        $(`#${scheduleIdDelete}`).remove()
        update_number_schedule(dayId, "subtraction")

    })
}

function active_delete_day() {
    $('button.delete-day').off('click')
    $('button.delete-day').click(function () {
        dayIdDelete = $(this).parent().attr('id')
        $(`#${dayIdDelete}`).remove()
    })
}


function update_number_schedule(target_day_id, add_or_sub) {
    inputNumSchedule = $(`div#${target_day_id} > input[name="number_of_schedule"]`)
    value = inputNumSchedule.attr("value")

    if (add_or_sub == "addition") {
        value = Number(value) + 1
    } else if (add_or_sub == "subtraction") {
        value = Number(value) - 1
    }
    inputNumSchedule.attr('value', value)
}


$(document).ready(function () {
    reactive_all_handler()
})