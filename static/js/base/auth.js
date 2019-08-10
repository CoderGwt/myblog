$(function () {
  let $img = $(".form-item .captcha-graph-img img");
  let sImageCodeId = "";  // 定义一个保存图像验证码的id
  let $username = $("#username");  // 用户名输入框
  let $mobile = $("#mobile");  // 手机号输入框

  // 校验用户名
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

  // 校验手机号
  $mobile.blur(function(){
    check_mobile();
  });

  function check_mobile(){
    let sMobile = $mobile.val();  // 获取到手机号
    let sReturnMsg = "";  // 保存返回值，发送短信的时候需要用到
    // 判断是否为空
    if(!sMobile){
      message.showError("手机号不能为空");
      return
    }

    // 判断是否符合手机号格式
    if (!(/^1[345789]\d{9}$/).test(sMobile)) {
      message.showError('手机号码格式不正确，请重新输入！');
      return
    }

    // 发起ajax请求
    $.ajax({
      url: "/verifications/mobiles/" + sMobile + "/",
      type: "GET",
      // dataType: "json",
      async: false,
      success: function (res) {
        if (res.data.count === 0){
          message.showSuccess("手机号可用");
          sReturnMsg = "success";
        }else{
          message.showError("手机号已被注册，请重新输入")
        }
      },
      fail: function (error) {
        message.showError("服务器繁忙，请稍后重试")
      }
    });
    return sReturnMsg;
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