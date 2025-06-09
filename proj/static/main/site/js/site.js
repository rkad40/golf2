"use strict";

$(document).ready(
    function () {

        // When scrolling down, update the active navbar tab as soon as the top of the screen enters the div 
        // upper waypoint.
        $('.waypoint-section-down').waypoint({
            handler: function (direction) {
                if (direction != 'down') return;
                let id = this.element.id;
                let sectionName = $(`#${id}`).attr('section-name');
                console.log(`${id}:${sectionName}:${direction}`);
                if (sectionName !== undefined) {
                    $(`.nav-item-section`).removeClass('active');
                    $(`#nav-item-${sectionName}`).addClass('active');
                }
            },
            offset: '20%',
        });

        // When scrolling up, update the active navbar tab as soon as 50% of the screen contains the div.
        $('.waypoint-section-up').waypoint({
            handler: function (direction) {
                if (direction != 'up') return;
                let id = this.element.id;
                let sectionName = $(`#${id}`).attr('section-name');
                console.log(`${id}:${sectionName}:${direction}`);
                if (sectionName !== undefined) {
                    $(`.nav-item-section`).removeClass('active');
                    $(`#nav-item-${sectionName}`).addClass('active');
                }
            },
            offset: '50%',
        });

        // When scroll size > 100px, add 'not-at-top' class to the navbar.  This is used to change the navbar from 
        // translucent to opaque.  
        let notYetScrolled = true;
        function scrollListener() {
			if ($(window).width() > 576) 
			{
				if ($(document).scrollTop() > 1) 
				{
					$(`#scroller`).slideUp(500);
					notYetScrolled = false;
				} 
				else 
				{
					if (!notYetScrolled) $(`#scroller`).slideDown(500);
				}
			}
            if ($(document).scrollTop() > 100) 
			{
                $(`.navbar`).addClass('not-at-top')
            } 
			else 
			{
                $(`.navbar`).removeClass('not-at-top')
            }
        };
        $(document).scroll(scrollListener);
        scrollListener();

        // This code allows for multidimensional dropdown menus.  
        $('.dropdown-menu a.dropdown-toggle').on('click', function (e) {
            if (!$(this).next().hasClass('show')) {
                $(this).parents('.dropdown-menu').first().find('.show').removeClass('show');
            }
            var $subMenu = $(this).next('.dropdown-menu');
            $subMenu.toggleClass('show');
            $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function (e) {
                $('.dropdown-submenu .show').removeClass('show');
            });
            return false;
        });


        // Render timeago elements.
        // $('time.timeago').timeago();
        $('.timeago').timeago();
        
        // Render Bootstrap tooltip and popover elements.
		$('[data-toggle="tooltip"]').tooltip();
        $('[data-toggle="popover"]').popover();

        // Start Bootstrap carousel elements.
        $('.carousel').carousel();

        // Render Animate on Scroll elements.
        initAnimateOnScroll();
		
		// Use flatpickr to render '.datetimeinput.form-control' elemnents.
		if (!IS_ADMIN) {
			$('.datetimeinput.form-control').flatpickr({
				enableTime: true,
				allowInput: true,
				defaultHour: 0,
			});		
		};

        // Crop images.
        cropImages();
		
		// Render media thumbnails for value defined inputs with class of thumbnail-img-source.
		$('.thumbnail-img-source').each(function() {
			let id = $(this).attr('id');
			MediaThumbnailImageSelected(id);
		});

        // Fade out the overlay.  The overlay is intended to allow HTML elements to fully render 
        // before being displayed.  
        $('.overlay').fadeOut(100);

        setTimeout(function() {
            // Crop images.
            cropImages();
        }, 50);
        setTimeout(function() {
			if ($(window).width() > 576) 
			{
				if ($(document).scrollTop() ==0 ) $(`#scroller`).slideDown(750);
			}
        }, 500);	
		
    }
);

function initAnimateOnScroll() {
	if (IS_ADMIN) return;
    AOS.init({
      duration: 1000,
      easing: "ease-in-out",
      once: true
    });
  }

function infoDialog(msg) {
    let dialog = new Dialog();
    dialog.Info(msg);
};

function errorDialog(msg) {
    let dialog = new Dialog();
    dialog.Error(msg);
};

function warningDialog(msg) {
    let dialog = new Dialog();
    dialog.Warning(msg);
};

function logOut() {
    let dialog = new Dialog()
    dialog.Launch({
        Title: 'Logout?',
        Icon: 'question',
        Width: 300,
        Height: 200,
        Content: 'Are you sure you want to log out?',
        Buttons: [{
                Name: `Yes`,
                Function: function () {
                    window.location.href = $('#user-logout-url').text();
                    dialog.Close();
                }
            },
            {
                Name: `No`,
                Function: dialog.Close,
            },
        ]
    });

};

function cropImages() {
    $('.crop-img > img').each(
        function () {
            let ww = $(this).parent().width();
            let wh = $(this).parent().height();
            let iw = $(this).width();
            let ih = $(this).height();
            console.log(`(${ww}, ${wh})`);
            console.log(`(${iw}, ${ih})`);
            let left = -1 * ((iw - ww) / 2);
            let top = -1 * ((ih - wh) / 2);
            if (left > 0) {
                $(this).css({
                    'width': `${ww}px`,
                    'height': 'auto'
                });
                let iw = $(this).width();
                let ih = $(this).height();
                left = -1 * ((iw - ww) / 2);
                top = -1 * ((ih - wh) / 2);
            }
            if (top > 0) {
                $(this).css({
                    'width': 'auto',
                    'height': `${wh}px`
                });
                let iw = $(this).width();
                let ih = $(this).height();
                left = -1 * ((iw - ww) / 2);
                top = -1 * ((ih - wh) / 2);
            }
            $(this).css({
                'top': top,
                'left': left
            });
        }
    )
};