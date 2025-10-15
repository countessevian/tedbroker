$(function () {


	/*****************Light Layout Start*****************/
	$(document).on("click", '#myonoffswitch1', function () {
		if (this.checked) {
			$('body').addClass('light-theme');
			$('#myonoffswitch3').prop('checked', true);
			$('#myonoffswitch6').prop('checked', true);
			$('body').addClass('dark-menu');
			$('body').removeClass('dark-theme');
			$('body').removeClass('color-header');
			$('body').removeClass('header-dark');
			$('body').removeClass('color-menu');
			localStorage.setItem('dashplexlighttheme', true);
			localStorage.removeItem("dashplexdarktheme");

			// remove light theme properties
			localStorage.removeItem('dashplexprimaryColor')
			localStorage.removeItem('dashplexprimaryHoverColor')
			localStorage.removeItem('dashplexprimaryBorderColor')
			document.querySelector('html')?.style.removeProperty('--dark-body');
			document.querySelector('html')?.style.removeProperty('--dark-theme');
			document.querySelector('html')?.style.removeProperty('--primary-bg-color');
			document.querySelector('html')?.style.removeProperty('--primary-hover-color');
			document.querySelector('html')?.style.removeProperty('--primary-border-color');

			// removing dark theme properties
			localStorage.removeItem('dashplexdarkPrimary')
			localStorage.removeItem('dashplexprimaryBorderColor')
			localStorage.removeItem('dashplexprimaryHoverColor')
			localStorage.removeItem('dashplexbgColor')
			localStorage.removeItem('dashplexdarktheme')

			$('#myonoffswitch1').prop('checked', true);
			$('#myonoffswitch5').prop('checked', false);
			$('#myonoffswitch8').prop('checked', false);

			const root = document.querySelector(':root');
			root.style = "";
			// names()valex
		} else {
			$('body').removeClass('lighttheme');
			localStorage.removeItem("dashplexlighttheme");
		}
		localStorageBackup();
		checkOptions();
	});

	
	/*****************Light Layout End*****************/

	/*****************Dark Layout Start*****************/
	$(document).on("click", '#myonoffswitch2', function () {
		if (this.checked) {
			$('body').addClass('dark-theme');
			$('#myonoffswitch5').prop('checked', true);
			$('#myonoffswitch8').prop('checked', true);
			$('body').removeClass('light-theme');
			$('body').removeClass('light-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('gradient-menu');
			$('body').removeClass('dark-header');
			$('body').removeClass('color-header');
			$('body').removeClass('light-header');
			localStorage.setItem('dashplexdarktheme', true);
			localStorage.removeItem("dashplexlighttheme");


			// remove light theme properties
			localStorage.removeItem('dashplexprimaryColor')
			localStorage.removeItem('dashplexprimaryHoverColor')
			localStorage.removeItem('dashplexprimaryBorderColor')
			localStorage.removeItem('dashplexdarkPrimary')
			document.querySelector('html')?.style.removeProperty('--primary-bg-color', localStorage.darkPrimary);
			document.querySelector('html')?.style.removeProperty('--primary-bg-hover', localStorage.darkPrimary);
			document.querySelector('html')?.style.removeProperty('--primary-bg-border', localStorage.darkPrimary);
			document.querySelector('html')?.style.removeProperty('--dark-primary', localStorage.darkPrimary);

			// removing light theme data 
			localStorage.removeItem('dashplexprimaryColor')
			localStorage.removeItem('dashplexprimaryHoverColor')
			localStorage.removeItem('dashplexprimaryBorderColor')

			$('#myonoffswitch3').prop('checked', false);
			$('#myonoffswitch6').prop('checked', false);
			//
			checkOptions();

			const root = document.querySelector(':root');
			root.style = "";
			names()
		} else {
			$('body').removeClass('dark-theme');
			localStorage.removeItem("dashplexdarktheme");
		}
		localStorageBackup()
	});
    /*****************Dark Layout End*****************/




	/*Light Menu Start*/
	$(document).on("click", '#myonoffswitch3', function () {
		if (this.checked) {
			$('body').addClass('light-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('dark-menu');
			localStorage.setItem("dashplexlightmenu", true);
			localStorage.removeItem("dashplexcolormenu");
			localStorage.removeItem("dashplexdarkmenu");
		} 
	});
	/*Light Menu End*/

	/*Color Menu Start*/
	$(document).on("click", '#myonoffswitch4', function () {
		if (this.checked) {
			$('body').addClass('color-menu');
			$('body').removeClass('dark-menu');
			$('body').removeClass('light-menu');
			localStorage.setItem("dashplexcolormenu", true);
			localStorage.removeItem("dashplexdarkmenu");
			localStorage.removeItem("dashplexlightmenu");
		} 
	});
	/*Color Menu End*/

	/*Dark Menu Start*/
	$(document).on("click", '#myonoffswitch5', function () {
		if (this.checked) {
			$('body').addClass('dark-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('light-menu');
			localStorage.setItem("dashplexdarkmenu", true);
			localStorage.removeItem("dashplexcolormenu");
			localStorage.removeItem("dashplexlightmenu");
		} 
	});
	/*Dark Menu End*/

	/*Light Header Start*/
	$(document).on("click", '#myonoffswitch6', function () {
		if (this.checked) {
			$('body').addClass('header-light');
			$('body').removeClass('color-header');
			$('body').removeClass('header-dark');
			localStorage.setItem("dashplexlightheader", true);
			localStorage.removeItem("dashplexcolorheader");
			localStorage.removeItem("dashplexdarkheader");
		} 
	});
	/*Light Header End*/

	/*Color Header Start*/
	$(document).on("click", '#myonoffswitch7', function () {
		if (this.checked) {
			$('body').addClass('color-header');
			$('body').removeClass('header-light');
			$('body').removeClass('header-dark');
			localStorage.setItem("dashplexcolorheader", true);
			localStorage.removeItem("dashplexlightheader");
			localStorage.removeItem("dashplexdarkheader");
		} 
	});
	/*Color Header End*/

	/*Dark Header Start*/
	$(document).on("click", '#myonoffswitch8', function () {
		if (this.checked) {
			$('body').addClass('header-dark');
			$('body').removeClass('color-header');
			$('body').removeClass('header-light');
			localStorage.setItem("dashplexdarkheader", true);
			localStorage.removeItem("dashplexlightheader");
			localStorage.removeItem("dashplexcolorheader");
		} 
	});
	/*Dark Header End*/

	/*****************Full Width Layout Start*****************/
	$(document).on("click", '#myonoffswitch9', function () {
		if (this.checked) {
			$('body').addClass('layout-fullwidth');
			if (document.querySelector('body').classList.contains('horizontal')  && !document.querySelector('body').classList.contains('login-img')) {
				checkHoriMenu();
			}
			$('body').removeClass('layout-boxed');
		}
	});
	/*****************Full Width Layout End*****************/

	/*****************Boxed Layout Start*****************/
	$(document).on("click", '#myonoffswitch10', function () {
		if (this.checked) {
			$('body').addClass('layout-boxed');
			if (document.querySelector('body').classList.contains('horizontal')) {
				checkHoriMenu();
			}
			$('body').removeClass('layout-fullwidth');
		}
	});
	/*****************Boxed Layout End*****************/

	/*****************Header-Position Styles Start*****************/
	$(document).on("click", '#myonoffswitch11', function () {
		if (this.checked) {
			$('body').addClass('fixed-layout');
			$('body').removeClass('scrollable-layout');
		}
	});
	$(document).on("click", '#myonoffswitch12', function () {
		if (this.checked) {
			$('body').addClass('scrollable-layout');
			$('body').removeClass('fixed-layout');
		}
	});
	/*****************Header-Position Styles End*****************/


	/*****************Default Sidemenu Start*****************/
	$(document).on("click", '#myonoffswitch13', function () {
		if (this.checked) {
			$('body').addClass('default-menu');
			hovermenu();
			$('body').removeClass('closed-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexdefaultmenu", true);
			localStorage.removeItem("dashplexclosedmenu");
			localStorage.removeItem("dashplexicontextmenu");
			localStorage.removeItem("dashplexsideiconmenu");
			localStorage.removeItem("dashplexhoversubmenu");
			localStorage.removeItem("dashplexhoversubmenu1");
		}
	});
	/*****************Default Sidemenu End*****************/


	/*****************Closed Sidemenu Start*****************/
	$(document).on("click", '#myonoffswitch16', function () {
		if (this.checked) {
			$('body').addClass('closed-menu');
			hovermenu();
			$('body').addClass('main-sidebar-hide');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexclosedmenu", true);
			localStorage.removeItem("dashplexdefaultmenu");
			localStorage.removeItem("dashplexicontextmenu");
			localStorage.removeItem("dashplexsideiconmenu");
			localStorage.removeItem("dashplexhoversubmenu");
			localStorage.removeItem("dashplexhoversubmenu1");
		} 
	});
	/*****************Closed Sidemenu End*****************/


	/*****************Hover Submenu Start*****************/
	$(document).on("click", '#myonoffswitch17', function () {
		if (this.checked) {
			$('body').addClass('hover-submenu');
			hovermenu();
			$('body').addClass('main-sidebar-hide');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexhoversubmenu", true);
			localStorage.removeItem("dashplexdefaultmenu");
			localStorage.removeItem("dashplexclosedmenu");
			localStorage.removeItem("dashplexicontextmenu");
			localStorage.removeItem("dashplexsideiconmenu");
			localStorage.removeItem("dashplexhoversubmenu1");
		}
	});
	/*****************Hover Submenu End*****************/

	/*****************Hover Submenu 1 Start*****************/
	$(document).on("click", '#myonoffswitch18', function () {
		if (this.checked) {
			$('body').addClass('hover-submenu1');
			hovermenu();
			$('body').addClass('main-sidebar-hide');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			localStorage.setItem("dashplexhoversubmenu1", true);
			localStorage.removeItem("dashplexdefaultmenu");
			localStorage.removeItem("dashplexclosedmenu");
			localStorage.removeItem("dashplexicontextmenu");
			localStorage.removeItem("dashplexsideiconmenu");
			localStorage.removeItem("dashplexhoversubmenu");
		}
	});
	/*****************Hover Submenu 1 End*****************/


	/*****************Icon Text Sidemenu Start*****************/
	$(document).on("click", '#myonoffswitch14', function () {
		if (this.checked) {
			$('body').addClass('icontext-menu');
			icontext();
			$('body').addClass('main-sidebar-hide');
			$('body').removeClass('default-menu');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexicontextmenu", true);
			localStorage.removeItem("dashplexdefaultmenu");
			localStorage.removeItem("dashplexclosedmenu");
			localStorage.removeItem("dashplexsideiconmenu");
			localStorage.removeItem("dashplexhoversubmenu");
			localStorage.removeItem("dashplexhoversubmenu1");

		}
	});
	/*****************Icon Text Sidemenu End*****************/

	/*****************Icon Overlay Sidemenu Start*****************/
	$(document).on("click", '#myonoffswitch15', function () {
		if (this.checked) {
			$('body').addClass('icon-overlay');
			hovermenu();
			$('body').addClass('main-sidebar-hide');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexsideiconmenu", true);
			localStorage.removeItem("dashplexdefaultmenu");
			localStorage.removeItem("dashplexclosedmenu");
			localStorage.removeItem("dashplexicontextmenu");
			localStorage.removeItem("dashplexhoversubmenu");
			localStorage.removeItem("dashplexhoversubmenu1");
		}
	});
	/*****************Icon Overlay Sidemenu End*****************/

	/* Vertical Menu Start */
	$(document).on("click", '#myonoffswitch01', function () {
		if (this.checked) {
			$('body').addClass('leftmenu');
			$('body').addClass('main-body');
			$('body').removeClass('horizontalmenu');
			$('body').removeClass('horizontalmenu-hover');
			$('.main-content').addClass('side-content');
			$('.main-header').removeClass(' hor-header');
			$('.main-header').addClass('sticky');
			$('.main-content').removeClass('hor-content');
			$('.main-container').removeClass('container');
			$('.main-container-1').removeClass('container');
			$('.main-container').addClass('container-fluid');
			$('.main-menu').removeClass('main-navbar hor-menu ');
			$('.main-menu').addClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').addClass('main-sidebar-header');
			$('.main-body-1').addClass('main-sidebar-body');
			$('.menu-icon').addClass('sidemenu-icon');
			$('.menu-icon').removeClass('hor-icon');
			localStorage.setItem("dashplexleftmenu", true);
			localStorage.removeItem("dashplexhorizontalmenuHover");
			localStorage.removeItem("dashplexhorizontalmenu");
			HorizontalHovermenu();
			ActiveSubmenu();
			var position = window.location.pathname.split('index-2.html');
			$(".main-menu li a").each(function () {
				var $this = $(this);
				var pageUrl = $this.attr("href");
				if (pageUrl) {
					if (position[position.length - 1] == pageUrl) {
						$(this).addClass("active");
						$(this).parent().prev().addClass("active"); // add active to li of the current link
						$(this).parent().parent().prev().addClass("active"); // add active class to an anchor
						$(this).parent().parent().parent().parent().prev().addClass("active");
						$(this).parent().parent().parent().parent().parent().addClass("is-expanded");
						$(this).parent().parent().prev().click(); // click the item to make it drop
						$(this).parent().parent().slideDown(300, function () { });
						$(this).parent().parent().parent().parent().slideDown(300, function () { });
						$(this).parent().parent().parent().parent().slideDown(300, function () { });
						return false;
					}
				}
			})

			} else {
				$('body').removeClass('leftmenu');
				$('body').addClass('horizontalmenu');
			}
	});
	/* Vertical Menu End */

	/* Horizontal Menu Start */
	$(document).on("click", '#myonoffswitch02', function () {
		if (this.checked) {
			if (window.innerWidth >= 992) {
				let subNavSub = document.querySelectorAll('.sub-nav-sub');
				subNavSub.forEach((e) => {
					e.style.display = '';
				})
				let subNav = document.querySelectorAll('.nav-sub')
				subNav.forEach((e) => {
					e.style.display = '';
				})
			}
			checkHoriMenu();
			$('body').addClass('horizontalmenu');
			$('body').removeClass('horizontalmenu-hover');
			$('body').removeClass('leftmenu');
			$('body').removeClass('main-body');
			$('.main-content').addClass('hor-content');
			$('.main-header').addClass('hor-header');
			$('.main-header').removeClass('sticky');
			$('.main-content').removeClass('side-content');
			$('.main-container').addClass('container');
			$('.main-container-1').addClass('container');
			$('.main-container').removeClass('container-fluid');
			$('.main-menu').addClass('main-navbar hor-menu');
			$('.main-menu').removeClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').removeClass('main-sidebar-header');
			$('.main-body-1').removeClass('main-sidebar-body');
			$('.menu-icon').removeClass('sidemenu-icon');
			$('.menu-icon').addClass('hor-icon');
			$('body').removeClass('default-menu');
			$('body').removeClass('closed-leftmenu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('main-sidebar-open');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexhorizontalmenu", true);
			localStorage.removeItem("dashplexhorizontalmenuHover");
			localStorage.removeItem("dashplexleftmenu");
			HorizontalHovermenu();
		} else {
			$('body').removeClass('horizontalmenu');
			$('body').addClass('leftmenu');
		}
	});
	/*Horizontal Menu End */

	/* Horizontal Hover Menu Start */
	$(document).on("click", '#myonoffswitch03', function () {
		if (this.checked) {
			if (window.innerWidth >= 992) {
				let subNavSub = document.querySelectorAll('.sub-nav-sub');
				subNavSub.forEach((e) => {
					e.style.display = '';
				})
				let subNav = document.querySelectorAll('.nav-sub')
				subNav.forEach((e) => {
					e.style.display = '';
				})
			}
			$('body').addClass('horizontalmenu');
			$('body').addClass('horizontalmenu-hover');
			$('body').removeClass('leftmenu');
			$('body').removeClass('main-body');
			$('.main-content').addClass('hor-content');
			$('.main-header').addClass('hor-header');
			$('.main-header').removeClass('sticky');
			$('.main-content').removeClass('side-content');
			$('.main-container').addClass('container');
			$('.main-container-1').addClass('container');
			$('.main-container').removeClass('container-fluid');
			$('.main-menu').addClass('main-navbar hor-menu');
			$('.main-menu').removeClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').removeClass('main-sidebar-header');
			$('.main-body-1').removeClass('main-sidebar-body');
			$('.menu-icon').removeClass('sidemenu-icon');
			$('.menu-icon').addClass('hor-icon');
			$('body').removeClass('default-menu');
			$('body').removeClass('closed-leftmenu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('main-sidebar-open');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			localStorage.setItem("dashplexhorizontalmenuHover", true);
			localStorage.removeItem("dashplexhorizontalmenu");
			localStorage.removeItem("dashplexleftmenu");
			if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
				checkHoriMenu();
				HorizontalHovermenu();
			}
		} else {
			$('body').removeClass('horizontalmenu');
			$('body').removeClass('horizontalmenu-hover');
			$('body').addClass('leftmenu');
		}
	});
	/* Horizontal Hover Menu End */


	//On ready function for Horizontal Menu
	$(function () {
		let bodyhorizontal = $('body').hasClass('horizontalmenu');
		if (bodyhorizontal) {
			if (window.innerWidth >= 992) {
				let subNavSub = document.querySelectorAll('.sub-nav-sub');
				subNavSub.forEach((e) => {
					e.style.display = '';
				})
				let subNav = document.querySelectorAll('.nav-sub')
				subNav.forEach((e) => {
					e.style.display = '';
				})
			}
			$('body').addClass('horizontalmenu');
			$('body').removeClass('leftmenu');
			$('body').removeClass('main-body');
			$('.main-content').addClass('hor-content');
			$('.main-header').addClass(' hor-header');
			$('.main-header').removeClass('sticky');
			$('.main-content').removeClass('side-content');
			$('.main-container').addClass('container');
			$('.main-container-1').addClass('container');
			$('.main-container').removeClass('container-fluid');
			$('.main-menu').addClass('main-navbar hor-menu');
			$('.main-menu').removeClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').removeClass('main-sidebar-header');
			$('.main-body-1').removeClass('main-sidebar-body');
			$('.menu-icon').removeClass('sidemenu-icon');
			$('.menu-icon').addClass('hor-icon');
			$('body').removeClass('default-menu');
			$('body').removeClass('closed-leftmenu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('main-sidebar-open');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
		}
		else {

		}
	});
	/***************** RTL*****************/
	$(document).on("click", '#myonoffswitch20', function () {
		if (this.checked) {
			$('body').addClass('rtl');
			$('body').removeClass('ltr');
			$("html[lang=en]").attr("dir", "rtl");
			$(".select2-container").attr("dir", "rtl");
			localStorage.setItem("dashplexrtl", true);
			localStorage.removeItem("dashplexltr");
			$("head link#style").attr("href", $(this));
			(document.getElementById("style")?.setAttribute("href", "assets/plugins/bootstrap/css/bootstrap.rtl.min.html"));

			var carousel = $('.owl-carousel');
			$.each(carousel, function (index, element) {
				// element == this
				var carouselData = $(element).data('owl.carousel');
				carouselData.settings.rtl = true; //don't know if both are necessary
				carouselData.options.rtl = true;
				$(element).trigger('refresh.owl.carousel');
			});
			if (document.querySelector('body').classList.contains('horizontal')  && !document.querySelector('body').classList.contains('login-img')) {
				checkHoriMenu();
			}
		}
	});
	/***************** RTL end*****************/

	/***************** LTR*****************/
	$(document).on("click", '#myonoffswitch19', function () {

		if (this.checked) {
			$('body').addClass('ltr');
			$('body').removeClass('rtl');
			$("html[lang=en]").attr("dir", "ltr");
			$(".select2-container").attr("dir", "ltr");
			localStorage.setItem("dashplexltr", true);
			localStorage.removeItem("dashplexrtl");
			$("head link#style").attr("href", $(this));
			(document.getElementById("style")?.setAttribute("href", "assets/plugins/bootstrap/css/bootstrap.min.html"));
			var carousel = $('.owl-carousel');
			$.each(carousel, function (index, element) {
				// element == this
				var carouselData = $(element).data('owl.carousel');
				carouselData.settings.rtl = false; //don't know if both are necessary
				carouselData.options.rtl = false;
				$(element).trigger('refresh.owl.carousel');
				if (document.querySelector('body').classList.contains('horizontal')  && !document.querySelector('body').classList.contains('login-img')) {
					checkHoriMenu();
				}
			});
		} else {
			$('body').removeClass('ltr');
			$('body').addClass('rtl');
			$(".select2-container").attr("dir", "rtl");
			localStorage.setItem("dashplexltr", "false");
			$("head link#style").attr("href", $(this));
			(document.getElementById("style")?.setAttribute("href", "assets/plugins/bootstrap/css/bootstrap.rtl.min.html"));
		}
	});
   /***************** LTR*****************/

});

$(function () {
	"use strict";
	
/***************** RTL Start*****************/


    //rtl has class
	if ($("body").hasClass("rtl")) {
		$('body').addClass('rtl');
		$('body').removeClass('ltr');
		$("html[lang=en]").attr("dir", "rtl");
		$(".select2-container").attr("dir", "rtl");
		// localStorage.setItem("dashplexrtl", true);
		// localStorage.removeItem("dashplexltr");
		$("head link#style").attr("href", $(this));
		(document.getElementById("style")?.setAttribute("href", "assets/plugins/bootstrap/css/bootstrap.rtl.min.html"));

		var carousel = $('.owl-carousel');
		$.each(carousel, function (index, element) {
			// element == this
			var carouselData = $(element).data('owl.carousel');
			carouselData.settings.rtl = true; //don't know if both are necessary
			carouselData.options.rtl = true;
			$(element).trigger('refresh.owl.carousel');
		});
		if (document.querySelector('body').classList.contains('horizontal')  && !document.querySelector('body').classList.contains('login-img')) {
			checkHoriMenu();
		}
	}


	// Horizontal Menu has class
	$(function () {
		let bodyhorizontal = $('body').hasClass('horizontalmenu');
		if (bodyhorizontal) {
			if (window.innerWidth >= 992) {
				let subNavSub = document.querySelectorAll('.sub-nav-sub');
				subNavSub.forEach((e) => {
					e.style.display = '';
					e.parentElement.classList.remove("show")
				})
				let subNav = document.querySelectorAll('.nav-sub')
				subNav.forEach((e) => {
					e.style.display = '';
					e.parentElement.classList.remove("show")
				})
			}
			$('body').addClass('horizontalmenu');
			$('body').removeClass('leftmenu');
			$('body').removeClass('main-body');
			$('.main-content').addClass('hor-content');
			$('.main-header').addClass(' hor-header');
			$('.main-header').removeClass('sticky');
			$('.main-content').removeClass('side-content');
			$('.main-container').addClass('container');
			$('.main-container-1').addClass('container');
			$('.main-container').removeClass('container-fluid');
			$('.main-menu').addClass('main-navbar hor-menu');
			$('.main-menu').removeClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').removeClass('main-sidebar-header');
			$('.main-body-1').removeClass('main-sidebar-body');
			$('.menu-icon').removeClass('sidemenu-icon');
			$('.menu-icon').addClass('hor-icon');
			$('body').removeClass('default-menu');
			$('body').removeClass('closed-leftmenu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('main-sidebar-open');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
		}
	});

	//Horizontal Menu hover has class
	$(function () {
		let bodyhorizontal = $('body').hasClass('horizontalmenu-hover');
		if (bodyhorizontal) {
			if (window.innerWidth >= 992) {
				let subNavSub = document.querySelectorAll('.sub-nav-sub');
				subNavSub.forEach((e) => {
					e.style.display = '';
				})
				let subNav = document.querySelectorAll('.nav-sub')
				subNav.forEach((e) => {
					e.style.display = '';
				})
			}
			checkHoriMenu();
			$('body').addClass('horizontalmenu');
			$('body').addClass('horizontalmenu-hover');
			$('body').removeClass('leftmenu');
			$('body').removeClass('main-body');
			$('.main-content').addClass('hor-content');
			$('.main-header').addClass('hor-header');
			$('.main-header').removeClass('sticky');
			$('.main-content').removeClass('side-content');
			$('.main-container').addClass('container');
			$('.main-container-1').addClass('container');
			$('.main-container').removeClass('container-fluid');
			$('.main-menu').addClass('main-navbar hor-menu');
			$('.main-menu').removeClass('main-sidebar main-sidebar-sticky side-menu');
			$('.main-container-1').removeClass('main-sidebar-header');
			$('.main-body-1').removeClass('main-sidebar-body');
			$('.menu-icon').removeClass('sidemenu-icon');
			$('.menu-icon').addClass('hor-icon');
			$('body').removeClass('default-menu');
			$('body').removeClass('closed-leftmenu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('main-sidebar-hide');
			$('body').removeClass('main-sidebar-open');
			$('body').removeClass('icon-overlay');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			HorizontalHovermenu();
		}
	});


	/***************** CLOSEDMENU HAs Class *********************/
	let bodyclosed = $('body').hasClass('closed-menu');
	if (bodyclosed) {
		$('body').addClass('closed-menu');
		$('body').addClass('main-sidebar-hide');
	}
	/***************** CLOSEDMENU HAs Class *********************/

	/***************** ICONOVERLAY MENU HAs Class *********************/
	let bodyiconoverlay = $('body').hasClass('icon-overlay');
	if (bodyiconoverlay) {
		$('body').addClass('icon-overlay');
		$('body').addClass('main-sidebar-hide');
	}
	/***************** ICONOVERLAY MENU HAs Class *********************/
	
	/***************** ICONTEXT MENU HAs Class *********************/
	let bodyicontext = $('body').hasClass('icontext-menu');
	if (bodyicontext) {
		if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
			icontext();
	}
	$('body').addClass('icontext-menu');
		$('body').addClass('main-sidebar-hide');
	}
	/***************** ICONTEXT MENU HAs Class *********************/

	/***************** HOVER-SUBMENU HAs Class *********************/
	let bodyhover = $('body').hasClass('hover-submenu');
	if (bodyhover) {
		$('body').addClass('hover-submenu');
		if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		hovermenu();
		}
		$('body').addClass('main-sidebar-hide');
	}
	/***************** HOVER-SUBMENU HAs Class *********************/

	/***************** HOVER-SUBMENU HAs Class *********************/
	let bodyhover1 = $('body').hasClass('hover-submenu1');
	if (bodyhover1) {
		$('body').addClass('hover-submenu1');
		if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		hovermenu();
		}
		$('body').addClass('main-sidebar-hide');
	}
	/***************** HOVER-SUBMENU HAs Class *********************/
	checkOptions();
})

function resetData() {
	'use strict'
	$('#myonoffswitch1').prop('checked', true);
	$('#myonoffswitch19').prop('checked', true);
	$('#myonoffswitch5').prop('checked', true);
	$('#myonoffswitch6').prop('checked', true);
	$('#myonoffswitch9').prop('checked', true);
	$('#myonoffswitch01').prop('checked', true);
	$('#myonoffswitch11').prop('checked', true);
	$('#myonoffswitch13').prop('checked', true);
	$('#myonoffswitch05').prop('checked', true);
	$('#myonoffswitch02').prop('checked', false);
	$('body')?.addClass('dark-menu');
	$('body')?.addClass('leftmenu');
	$('body')?.addClass('main-body');
	$('body')?.removeClass('dark-theme');
	$('body')?.removeClass('light-menu');
	$('body')?.removeClass('color-menu');
	$('body')?.removeClass('gradient-menu');
	$('body')?.removeClass('header-dark');
	$('body')?.removeClass('gradient-header');
	$('body')?.removeClass('light-header');
	$('body')?.removeClass('color-header');
	$('body')?.removeClass('layout-boxed');
	$('body')?.removeClass('icontext-menu');
	$('body')?.removeClass('icon-overlay');
	$('body')?.removeClass('closed-menu');
	$('body')?.removeClass('hover-submenu');
	$('body')?.removeClass('hover-submenu1');
	$('body')?.removeClass('scrollable-layout');
	$('body')?.removeClass('main-sidebar-hide');
	// responsive();

	$('body').addClass('ltr');
	$('body').removeClass('rtl');
	$("html[lang=en]").attr("dir", "ltr");
	$(".select2-container").attr("dir", "ltr");
	localStorage.setItem("dashplexltr", true);
	localStorage.removeItem("dashplexrtl");
	$("head link#style").attr("href", $(this));
	(document.getElementById("style")?.setAttribute("href", "assets/plugins/bootstrap/css/bootstrap.min.html"));
	var carousel = $('.owl-carousel');
	$.each(carousel, function (index, element) {
		// element == this
		var carouselData = $(element).data('owl.carousel');
		carouselData.settings.rtl = false; //don't know if both are necessary
		carouselData.options.rtl = false;
		$(element).trigger('refresh.owl.carousel');
		if (document.querySelector('body').classList.contains('horizontal')  && !document.querySelector('body').classList.contains('login-img')) {
			checkHoriMenu();
		}
	});
	
	
	$('body').removeClass('horizontalmenu');
	$('body').removeClass('horizontalmenu-hover');
	$('.main-content').addClass('side-content');
	$('.main-header').removeClass(' hor-header');
	$('.main-header').addClass('sticky');
	$('.main-content').removeClass('hor-content');
	$('.main-container').removeClass('container');
	$('.main-container-1').removeClass('container');
	$('.main-container').addClass('container-fluid');
	$('.main-menu').removeClass('main-navbar hor-menu ');
	$('.main-menu').addClass('main-sidebar main-sidebar-sticky side-menu');
	$('.main-container-1').addClass('main-sidebar-header');
	$('.main-body-1').addClass('main-sidebar-body');
	$('.menu-icon').addClass('sidemenu-icon');
	$('.menu-icon').removeClass('hor-icon');
	localStorage.setItem("dashplexleftmenu", true);
	localStorage.removeItem("dashplexhorizontalmenuHover");
	localStorage.removeItem("dashplexhorizontalmenu");
	HorizontalHovermenu();
	ActiveSubmenu();
	var position = window.location.pathname.split('index-2.html');
	$(".main-menu li a").each(function () {
		var $this = $(this);
		var pageUrl = $this.attr("href");
		if (pageUrl) {
			if (position[position.length - 1] == pageUrl) {
				$(this).addClass("active");
				$(this).parent().prev().addClass("active"); // add active to li of the current link
				$(this).parent().parent().prev().addClass("active"); // add active class to an anchor
				$(this).parent().parent().parent().parent().prev().addClass("active");
				$(this).parent().parent().parent().parent().parent().addClass("is-expanded");
				$(this).parent().parent().prev().click(); // click the item to make it drop
				$(this).parent().parent().slideDown(300, function () { });
				$(this).parent().parent().parent().parent().slideDown(300, function () { });
				$(this).parent().parent().parent().parent().slideDown(300, function () { });
				return false;
			}
		}
	})
}


function checkOptions() {
	'use strict'

	//  dark-theme 
	if (document.querySelector('body').classList.contains('dark-theme')) {
		$('#myonoffswitch2').prop('checked', true);
	}
	// horizontalmenu
	if (document.querySelector('body').classList.contains('horizontalmenu')) {
		$('#myonoffswitch02').prop('checked', true);
	}

	// horizontalmenu-hover
	if (document.querySelector('body').classList.contains('horizontalmenu-hover')) {
		$('#myonoffswitch03').prop('checked', true);
	}

	//RTL 
	if (document.querySelector('body').classList.contains('rtl')) {
		$('#myonoffswitch20').prop('checked', true);
	}

	// light header 
	if (document.querySelector('body').classList.contains('header-light')) {
		$('#myonoffswitch6').prop('checked', true);
	}
	// color header 
	if (document.querySelector('body').classList.contains('color-header')) {
		$('#myonoffswitch7').prop('checked', true);
	}
	// dark header 
	if (document.querySelector('body').classList.contains('header-dark')) {
		$('#myonoffswitch8').prop('checked', true);
	}

	// light menu
	if (document.querySelector('body').classList.contains('light-menu')) {
		$('#myonoffswitch3').prop('checked', true);
	}
	// color menu
	if (document.querySelector('body').classList.contains('color-menu')) {
		$('#myonoffswitch4').prop('checked', true);
	}
	// dark menu
	if (document.querySelector('body').classList.contains('dark-menu')) {
		$('#myonoffswitch5').prop('checked', true);
	}
	//  default-menu 
	if (document.querySelector('body').classList.contains('default-menu')) {
		$('#myonoffswitch13').prop('checked', true);
	}
	// icontext-menu 
	if (document.querySelector('body').classList.contains('icontext-menu')) {
		$('#myonoffswitch14').prop('checked', true);
	}
	// icon-overlay 
	if (document.querySelector('body').classList.contains('icon-overlay')) {
		$('#myonoffswitch15').prop('checked', true);
	}
	// closed menu
	if (document.querySelector('body').classList.contains('closed-menu')) {
		$('#myonoffswitch16').prop('checked', true);
	}
	//  hover-submenu 
	if (document.querySelector('body').classList.contains('hover-submenu')) {
		$('#myonoffswitch17').prop('checked', true);
	}
	//  hover-submenu1 
	if (document.querySelector('body').classList.contains('hover-submenu1')) {
		$('#myonoffswitch18').prop('checked', true);
	}
}

checkOptions()
	/***************** Add Switcher Classes *********************/
	//LTR & RTL
	if (!localStorage.getItem('dashplexrtl') && !localStorage.getItem('dashplexltr')) {

		/***************** RTL *********************/
		// $('body').addClass('rtl');
		/***************** RTL *********************/
		/***************** LTR *********************/
		// $('body').addClass('ltr');
		/***************** LTR *********************/

	}
	//Light-mode & Dark-mode
	if (!localStorage.getItem('dashplexlight') && !localStorage.getItem('dashplexdark')) {
		/***************** Light THEME *********************/
		// $('body').addClass('light-theme');
		/***************** Light THEME *********************/

		/***************** DARK THEME *********************/
		// $('body').addClass('dark-theme');
		// $('body').removeClass('light-theme');
		/***************** Dark THEME *********************/
	}

	//Vertical-menu & Horizontal-menu
	if (!localStorage.getItem('dashplexvertical') && !localStorage.getItem('dashplexhorizontalmenu') && !localStorage.getItem('dashplexhorizontalmenuHover')) {
		/* Horizontal Menu Start */
			// $('body').addClass('horizontalmenu');
			// if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
			// 	checkHoriMenu();
			// }
		/*Horizontal Menu End */

		/***************** Horizontal-Hover THEME *********************/
		// $('body').addClass('horizontalmenu-hover');
		// if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		// 	checkHoriMenu();
		// }
		/***************** Horizontal-Hover THEME *********************/
	}

	//Vertical Layout Style
	if (!localStorage.getItem('dashplexdefaultmenu') && !localStorage.getItem('dashplexclosedmenu') && !localStorage.getItem('dashplexicontextmenu')&& !localStorage.getItem('dashplexsideiconmenu')&& !localStorage.getItem('dashplexhoversubmenu')&& !localStorage.getItem('dashplexhoversubmenu1')) {
		/**Default-Menu**/
		// $('body').addClass('default-menu');
		/**Default-Menu**/

		/**closed-Menu**/
		// $('body').addClass('closed-menu');
		// $('body').addClass('main-sidebar-hide');
		/**closed-Menu**/

		/**Icon-Text-Menu**/
		// $('body').addClass('icontext-menu');
		// $('body').addClass('main-sidebar-hide');
		// if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		// 		icontext();
		// }

		/**Icon-Text-Menu**/

		/**Icon-Overlay-Menu**/
		// $('body').addClass('icon-overlay');
		// $('body').addClass('main-sidebar-hide');
		/**Icon-Overlay-Menu**/

		/**Hover-Sub-Menu**/
		// $('body').addClass('hover-submenu');
		// $('body').addClass('main-sidebar-hide');
		// if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		// 	hovermenu();
		// }
		/**Hover-Sub-Menu**/

		/**Hover-Sub-Menu1**/
		// $('body').addClass('hover-submenu1');
		// $('body').addClass('main-sidebar-hide');
		// if(document.querySelector('.page').classList.contains('main-signin-wrapper') !== true){
		// 	hovermenu();
		// }
		/**Hover-Sub-Menu1**/
	}

	//Boxed Layout Style
	if (!localStorage.getItem('dashplexfullwidth') && !localStorage.getItem('dashplexboxedwidth')) {
	// $('body').addClass('layout-boxed');
	}

	//Scrollable-Layout Style
	if (!localStorage.getItem('dashplexfixed') && !localStorage.getItem('dashplexscrollable')) {
		/* Header-Scrollable Start */
			// $('body').addClass('scrollable-layout');
		/* Header-Scrollable End */

		/* Header-Fixed Start */
			// $('body').addClass('fixed-layout');
		/* Header-Fixed End */
	}


	//Menu Styles
	if (!localStorage.getItem('dashplexlightmenu') && !localStorage.getItem('dashplexcolormenu') && !localStorage.getItem('dashplexdarkmenu') && !localStorage.getItem('dashplexgradientmenu')) {
		/**Light-menu**/
		// $('body').addClass('light-menu');
		// $('body').removeClass('dark-menu');
		/**Light-menu**/

		/**Color-menu**/
		// $('body').addClass('color-menu');
		// $('body').removeClass('dark-menu');
		/**Color-menu**/

		/**Dark-menu**/
		// $('body').addClass('dark-menu');
		/**Dark-menu**/
	}
	//Header Styles
	if (!localStorage.getItem('dashplexlightheader') && !localStorage.getItem('dashplexcolorheader') && !localStorage.getItem('dashplexdarkheader') && !localStorage.getItem('dashplexgradientheader')) {
		/**Light-Header**/
		// $('body').addClass('header-light');
		/**Light-Header**/

		/**Color-Header**/
		// $('body').addClass('color-header');
		/**Color-Header**/


		/**Dark-Header**/
		// $('body').addClass('header-dark');
		/**Dark-Header**/

	}
	/***************** Add Switcher Classes *********************/
	