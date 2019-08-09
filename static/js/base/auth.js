$(function () {
  let $img = $(".form-item .captcha-graph-img img");
  let sImageCodeId = "";  // 定义一个保存图像验证码的id
  let $username = $("#username");

  $username.blur(function () {
    check_username();
  });
  function check_username() {
    let username = $username.val();
    if (username === "") {
      // alert("用户名不能为空！");
      message.showError('用户名不能为空！');
      return
    }
    if (!(/^\w{5,20}$/).test(username)) {
      // alert("请输入5-20个字符的用户名");
      message.showError('请输入5-20个字符的用户名');
      return
    }

    $.ajax({
      url: "/verifications/username/" + username + "/",
      type: 'GET' ,
      dataType: "json",
      success: function (res) {
        console.log(res);
        if(res.data.count === 0){
          message.showInfo(res.data.msg);
        }else{
          message.showError(res.data.msg)
        }
        // alert(res.data.msg);  // 后端通过to_json_data封装返回信息
        // alert(res.msg);  // 后端直接返回的是JsonResponse
        // if(res.count == 0){
        //   alert("可用")
        // }else{
        //   alert("不可可用")
        // }
      },
      fail: function(error){
        // alert(error);
        message.showError("服务器错误，请稍后充实")
      }
    })


  }


  generateImageCode();  // 生成图片验证码
  $img.click(generateImageCode); // 点击验证码生成新的图片验证码 （不需要加括号，直接函数名即可）

  // 生成图片UUID验证码
  function generateUUID() {
    let d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
  }

  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
  function generateImageCode() {
    // 1、生成一个图片验证码随机编号
    sImageCodeId = generateUUID();
    // 2、拼接请求url /image_codes/<uuid:image_code_id>/
    let imageCodeUrl = "/verifications/image_code/" + sImageCodeId + "/";
    // 3、修改验证码图片src地址
    $img.attr('src', imageCodeUrl)


  }
});