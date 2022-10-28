// window.jsPDF = window.jspdf.jsPDF

var updateAnyThing = false


var opt = {
    margin: [6, 6, 20, 6],
    image: { type: 'jpeg', quality: 1 },
    html2canvas: { dpi: 72, scale: 2, },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pageBreak: { mode: 'css', after: '.break-page' }

}

$(document).ready(function () {

    $('textarea.inclusion-and-exclusion').each(function () {
        content = $(this).parent().find('input').val()
        $(this).text($(`#${content}`).text())
    })

    // if content changed, alert before leaving page
    $(window).bind('beforeunload', function () {
        if (updateAnyThing) {
            return 'Are you sure you want to leave?';
        }
    });

    // quote generation
    $('#download').click(function () {

        $("div.quote-page").removeClass("border border-secondary")
        $('.print-hidden').attr('hidden', true)

        fileName = $('#quoteNumber').text()

        var quote = document.getElementById('quote');
        html2pdf().set(opt).from(quote).toPdf().get('pdf').then((pdf) => {

            var totalPages = pdf.internal.getNumberOfPages()
            for (var i = 1; i <= totalPages; i++) {
                pdf.setPage(i)
                pdf.setFontSize(10).setTextColor(150, 150, 150)
                footer = 'Wildman Ecological Preservation | info@taiwanbirdguide.com | +886 2 2599 1783 |'

                pdf.text(footer, (pdf.internal.pageSize.getWidth() / 2), pdf.internal.pageSize.getHeight() - 10, 'center');
            }

        }).save(fileName + '.pdf')

    })

    // recovering borders and edit buttons
    $("#recover").click(function () {
        $("div.quote-page").removeClass("border border-secondary")
        $("div.quote-page").addClass("border border-secondary")
        $('.print-hidden').removeAttr('hidden')
    })

    // live update description
    $("textarea.description").on('keyup paste', function () {
        description = $(this).val()
        serialNumber = $(this).parent().find("input[disabled!='disabled']").val()
        console.log(serialNumber)
        $(`#${serialNumber} > p`).text(description)
        updateAnyThing = true
    })

    // live update inclusion and exclusion
    $('textarea.inclusion-and-exclusion').on('keyup paste', function () {
        content = $(this).val()
        contentId = $(this).parent().find("input").val()
        $(`#${contentId}`).text(content)
        updateAnyThing = true
    })

    // live selection show
    $('.form-check-input').on('change', function () {
        isChecked = $(this).is(":checked")
        sctionId = $(this).parent().find("input[type='hidden']").val()

        if (isChecked) {
            $(`#${sctionId}`).removeAttr('hidden')
        } else {
            $(`#${sctionId}`).attr('hidden', true)
        }

    })

    // change language
    $('#langSelect').on('change', function () {
        lang = $(this).val()
        if (lang == 'chinese') {
            $('.chinese').removeAttr("hidden")
            $('.english').attr("hidden", true)
            $('input.chinese').removeAttr("disabled")
            $('input.english').attr("disabled", true)

        } else {
            $('.english').removeAttr("hidden")
            $('.chinese').attr("hidden", true)
            $('input.english').removeAttr("disabled")
            $('input.chinese').attr("disabled", true)
        }
    })

})
