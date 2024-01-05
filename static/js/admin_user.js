{
    // -----------------------EVENT HANDLERS---------------------

    function onCopyBtnClickHandler() {
        let userId = $(".user-id").text();
        let $tempInput = $("<input>");
        $("body").append($tempInput);
        $tempInput.val(userId);
        $tempInput.select();
        document.execCommand("copy");

        $tempInput.remove();
        $(".copy-id-btn").text("Done!");
    }

    function onDeleteListingsBtnClickHandler(event) {
        event.stopPropagation();
        event.preventDefault();
        window.location.href = `/admin/listings/destroy/${event.target.id}`;
    }

    function onDeleteUserBtnClickHandler() {
        $(".delete-popup-container").css("display", "flex");
    }

    function onNoClickHandler() {
        $(".delete-popup-container").css("display", "none");
    }
    function onYesClickHandler(event) {
        window.location.href = `/admin/users/destroy/${event.target.id}`;
    }

    function onListingItemClickHandler(event) {
        event.stopPropagation();
        window.location.href = `/listings/fetch/${event.target.id}`;
    }

    function onDeleteContainerClickListener(event) {
        event.stopPropagation();
        $(".delete-popup-container").css("display", "none");

    }

    function onDeletePopupClickListener(event) {
        event.stopPropagation();
    }


    // -----------------------EVENT LISTENERS---------------------

    $(".copy-id-btn").click(onCopyBtnClickHandler);
    $(".delete-item").click(onDeleteListingsBtnClickHandler);
    $(".delete-user-btn").click(onDeleteUserBtnClickHandler);
    $(".delete-popup>img").click(onNoClickHandler);
    $(".option-yes").click(onYesClickHandler);
    $(".option-no, .delete-popup-container").click(onNoClickHandler);
    $(".item-container").click(onListingItemClickHandler);
    $(".delete-popup").click(onDeletePopupClickListener);

}
