$(function(){


    // PROFILE PAGE

    // TAB SWITCH
    $('.profile-tab').click(function(){
        $('.profile-tab').removeClass('active-tab');
        $('.tab-content').removeClass('active-content');

        $(this).addClass('active-tab');
        var target = $(this).data('tab');
        '#tab-' + target;
        $('#tab-' + target).addClass('active-content');
    });

    $('.ed-tab').click(function(){
        $('.ed-tab').removeClass('active-ed-tab');
        $('.ed-tab-content').removeClass('active-ed-content');

        $(this).addClass('active-ed-tab');
        var target = $(this).data('tab');
        '#ed-tab-' + target;
        $('#ed-tab-' + target).addClass('active-ed-content');
    });

  
    
    // FOLLOW BUTTON TOGLE
    $('.btn-follow').click(function(){
        var following = $(this).hasClass('btn-following')
        if(following){
            $(this).text('Follow').removeClass('btn-following')
        }else{
            $(this).text('Following').addClass('btn-following')
        }
    });

    // LIKE BUTTON - send AJAX to server to toggle like/unlike
    $('.like-btn').click(function(){
        var btn = $(this);
        var icon = btn.find('i');
        var count = btn.find('span');
        var postId = btn.data('post-id');

        if(!postId){
            return;
        }

        var wasLiked = icon.hasClass('fa-solid');

        $.ajax({
            url: '/like-post/' + postId + '/',
            method: 'POST',
            dataType: 'json'
        }).done(function(resp){
            if(resp && resp.success){
                if(resp.liked){
                    icon.removeClass('fa-regular').addClass('fa-solid').css('color','#ef4444');
                }else{
                    icon.removeClass('fa-solid').addClass('fa-regular').css('color','');
                }
                count.text(resp.like_count);
            }else{
                var msg = (resp && resp.message) ? resp.message : 'Could not update like';
                alert(msg);
            }
        }).fail(function(xhr){
            var msg = 'An error occurred';
            if(xhr.status === 401){
                msg = 'You must be logged in to like posts';
            } else if(xhr.responseJSON && xhr.responseJSON.message){
                msg = xhr.responseJSON.message;
            }
            alert(msg);
            // no UI change since we wait for server response
        });
    })

    

    $('#attachEventBtn').click(function(){
        $('#composerEventStrip').slideToggle()
        $('#eventSearchWrap').slideToggle()
    });
  

   $('#imageInput').change(function(){
        
        var files = this.files;

        if(files.length < 1){
            return;
        }
        $('#mediaPreviewRow').show();
        for(var a=0; a<files.length; a++){
            var reader = new FileReader();
            reader.onload = function(e){
                $('#mediaPreviewRow').append('<div class="media-preview-item"><img src="' + e.target.result + '"><button class="remove-media-btn"><i class="fa-solid fa-xmark"></i></button></div>')
            }
            var file = files[a]
            reader.readAsDataURL(file);
        $('.composer-post-btn').prop('disabled', false);
   }});

   $('#videoInput').change(function(){
        
        var file = this.files[0];
        var url = URL.createObjectURL(file);

        if(!file){
            return;
        }

    
        $('#mediaPreviewRow').show();
   
        $('#mediaPreviewRow').append('<div class="media-preview-item"><video src="' + url + '" controls></video><button class="remove-media-btn"><i class="fa-solid fa-xmark"></i></button></div>')
   
        $('.composer-post-btn').prop('disabled', false);
   });

   $('.follow-small-btn').click(function(){
        var following = $(this).hasClass('btn-following');
        var num = Number($(this).closest('.creator-item').find('.follower-small-btn').text());


        if(following){
            $(this).removeClass('btn-following').text('Follow')
            num = num - 1;
            $(this).closest('.creator-item').find('.follower-small-btn').text(num)
        }
        else{
            $(this).addClass('btn-following').text('Following')
            num = num + 1;
            $(this).closest('.creator-item').find('.follower-small-btn').text(num)
        }
    });
});

$(document).on('click', '.remove-media-btn', function(){
    $(this).closest('.media-preview-item').remove();
    if($('#mediaPreviewRow').children().length === 0){
        $('#mediaPreviewRow').hide();
    }
});

   $(function() {

    // SIDEBAR TOGGLE
    $('#sidebarToggle').on('click', function() {
       
        $('#sidebar').toggleClass('sidebar-open');
        $('#sidebarOverlay').toggleClass('overlay-active');
        
    });

    // CLOSE when clicking overlay
    $('#sidebarOverlay').on('click', function() {
        $('#sidebar').removeClass('sidebar-open');
        $(this).removeClass('overlay-active');
    });

    // CLOSE when a nav link is clicked on mobile
    $('#sidebar .sidebar-nav a').on('click', function() {
        if ($(window).width() <= 768) {
            $('#sidebar').removeClass('sidebar-open');
            $('#sidebarOverlay').removeClass('overlay-active');
        }
    });

    // RESET on resize back to desktop
    $(window).on('resize', function() {
        if ($(window).width() > 768) {
            $('#sidebar').removeClass('sidebar-open');
            $('#sidebarOverlay').removeClass('overlay-active');
        }
    });

});

$(function(){
    $('#searchInput').on('input', function(){
        var search = $(this).val().toLowerCase().trim();
        var eventCards = $('.dis-event-card');

        for(var a=0; a<eventCards.length; a++){
            var card = $(eventCards[a]);
            var eventTitle = card.find('.event-title').text().toLowerCase();
            var commTitle = card.find('.community-title').text().toLowerCase();
            var match = eventTitle.includes(search) || commTitle.includes(search);
            
            card.parent().toggle(match);
        }
        if(match in event-section-top === false){
            $('event-section-top').hide();
        }
        if(match in comm-section-top === false){
            $('comm-section-top').hide();
        }
        
    });
});

//Comm- search
$(document).ready(function(){
        $('#commSearch').on('input', function(){
        var search = $(this).val().toLowerCase().trim()
        var commCards = $('.dis-comm');

        for(s=0; s<commCards.length; s++){
            var card = $(commCards[s]);
            var commName =card.find('.commName').text().toLowerCase()
            var match = commName.includes(search)
            
            card.parent().toggle(commName.includes(search))
        }
        });

        //Crad filter
        $('.category-pill').click(function(){
            var catName = $(this).text().toLowerCase()
            // alert('You clicked ' + catName)
            $('.category-pill').removeClass('active-pill')
            $(this).addClass('active-pill')

            var badges = $('.dis-comm')

            for(b=0; b<=badges.length; b++){
                var badge = $(badges[b])
                var badgeName = badge.find('.comm-category-badge').text().toLowerCase()
                var match = catName == badgeName;

                
                if(catName != 'all'){
                    badge.parent().toggle(match)
                }
                else{
                    badge.parent().show()
                }
            }
        });
        // $('.cm-reply-trigger').on('click', function() {
        // var username = $(this).data('username');
        // var cmId = $(this).closest('.cm-item').attr('id');
        // var replyWrap = $('#reply-' + cmId);

        // $('.cm-reply-input-wrap').not(replyWrap).hide();
        // replyWrap.toggle();

        // if (replyWrap.is(':visible')) {
        //     replyWrap.find('.cm-reply-input').focus();
        // }
    // });
    });