{

  // --------------------CLICK HANDLER--------------------

  function dropDownClickHandler(event) {
    let height = $(".drop-navigation-list").height();
    if (height > 1) {
      $(".drop-navigation-list").css("height", "0");
      $(".drop-down>img").css("transform", "rotate(0deg)");
    } else {
      $(".drop-navigation-list").css("height", "70px");
      $(".drop-down>img").css("transform", "rotate(180deg)");
    }
    console.log(height);
  }


  // ---------------------CLICK LISTENERS--------------
  $(".drop-down").click(dropDownClickHandler);

}