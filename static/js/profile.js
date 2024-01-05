{
    $(".item-container").click(event => {
        let id = event.target.id;
        if (id) window.location.href = `/listings/fetch/${id}`;
    })
}