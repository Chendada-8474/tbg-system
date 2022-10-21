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
const reOrderButton = document.getElementById("reorder");


//  reset the orderation od days
reOrderButton.addEventListener("click", function () {
    first_day = 1
    var days = divItinerary.children
    for (let index = 0; index < days.length; index++) {
        const element = days[index];
        var labelText = element.getElementsByTagName('label')
        labelText[0].textContent = "Day " + first_day++
    }
})

function reactive_all_handler() {
    active_spot_change()
    active_accommodation_change()
    active_add_day_click()
    active_add_schedule()
    active_delete_day()
    active_delete_schedule()
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
        deleteButton = $("#schedule1").find('button.delete-schedule').clone()
        newDay.find('div.card-header').text('New Spot').append(deleteButton)

        newDay.find('button.delete-day').removeAttr('disabled')

        newDay.find('input[name="number_of_schedule"]').attr('value', 1)

        $('#days').append(newDay)

        dayCount += 1
        scheduleCount += 1
        active_spot_change()
        active_accommodation_change()
        active_add_schedule()
        active_delete_schedule()
        active_delete_day()
        $(".schedule").sortable();
    })
}



function active_add_schedule() {
    $(".add-schedule").off('click')
    $(".add-schedule").click(function () {

        dayId = $(this).parent().parent().attr('id')
        newCard = $("#schedule1").clone().attr("id", `schedule${scheduleCount}`)
        deleteButton = newCard.find('button.delete-schedule').clone().removeAttr('disabled')
        newCard.find("div.card-header").text("New Spot").append(deleteButton)
        scheduleCount += 1

        $(`#${dayId}`).find("div.schedule").append(newCard)

        update_number_schedule(dayId, "addition")

        active_spot_change()
        active_add_day_click()
        active_delete_schedule()
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
    console.log(target_day_id, value, add_or_sub)
}



$(document).ready(function () {
    reactive_all_handler()
})