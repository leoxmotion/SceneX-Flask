$(function(){
    var $body = $(document.body);

    // Feed & composer interactions
    $('#composerPostBtn').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('composer');
        var myform = new FormData(form);
        $.ajax({
            url: '/create-post/',
            type: 'POST',
            data: myform,
            success: function(){
                document.location.href='/home/';
            },
            error: function(err){console.log(err);}
        });
    });

     $('#commPostBtn').on('click', function(event){
        event.preventDefault();

        var form = document.getElementById('comm');
        var myform = new FormData(form);
        var commId = $('#comm').data('comm-id');


        $.ajax({
            url: '/create-comm-post/' + commId+ '/',
            type: 'POST',
            data: myform,
            processData: false,
            contentType: false,

            success: function(){
                document.location.href='/comm_detail/' + commId+ '/';
            },
            error: function(err){console.log(err);}
        });
    });
    

    $('#sendComment').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('commentInput');
        var myform = new FormData(form);

        $.ajax({
            url: '/comments/' + window.post_id + '/',
            type: 'POST',
            data: myform,
            processData: false,
            contentType: false,
            success: function(){
                document.location.href='/comments/' + window.post_id;
                $('#commentbox').val('');
            },
            error: function(err){console.log(err);}
        });
    });

    $('#sendCommComment').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('commCommentInput');
        var myform = new FormData(form);

        $.ajax({
            url: '/community/comments/' + window.post_id,
            type: 'POST',
            data: myform,
            processData: false,
            contentType: false,
            success: function(){
                document.location.href='/community/comments/' + window.post_id;
                $('#commentbox').val('');
            },
            error: function(err){console.log(err);}
        });
    });

    $('.ce-publish-btn').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('commForm');
        var data2send = new FormData(form);
        $.ajax({
            url: '/create_community/',
            type: 'POST',
            data: data2send,
            success: function(resp){
                alert(resp);
                document.location.href='/creator/communities/';
            },
            error: function(err){console.log(err);}
        });
    });

    $('.ce-edit-btn').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('commEditForm');
        var data2send = new FormData(form);
        let commId = $(this).data("edit-comm");
        $.ajax({
            url: '/creator/edit-community/' + commId + '/',
            type: 'POST',
            data: data2send,
            success: function(resp){
                alert(resp);
                document.location.href='/creator/communities/';
            },
            error: function(err){console.log(err);}
        });
    });

    $('.ep-save-btn').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('editForm');
        var data2send = new FormData(form);
     
        $.ajax({
            url: '/change-profile/',
            type: 'POST',
            data: data2send,
            error: function(err){console.log(err);},
            success: function(resp){alert(resp);}
        });
    });

    // Media uploader interactions
    $('#uploadImageBtn').on('click', function(){
        $('#imageInput').trigger('click');
    });

    $('[data-open-comment]').on('click', function(){
        var postId = $(this).data('open-comment');
        $('#openComment' + postId).trigger('click');
    });

    $('[data-view-event]').on('click', function(){
        var eventId = $(this).data('view-event');
        $('#viewEvent' + eventId).trigger('click');
    });

    $('#editProfileBtn').on('click', function(){
        $('#editProfile').trigger('click');
    });

    $('#readMoreBtn').on('click', function(){
        var $desc = $('#edDescription');
        var $full = $('#edFullDesc');
        if ($full.length) {
            $full.slideToggle();
            $desc.toggleClass('is-expanded');
        }
    });

    $('#rsvpBtn').on('click', function(){
        $(this).toggleClass('is-active');
        $(this).find('i').toggleClass('fa-bolt fa-check');
    });

    $('.ed-sidebar-rsvp [data-trigger="edit-event"]').on('click', function(){
        $('#edit').trigger('click');
    });

    $('.ed-sidebar-rsvp [data-trigger="add-tickets"]').on('click', function(){
        $('#addTickets').trigger('click');
    });

    $('.ed-sidebar-rsvp [data-trigger="delete-event"]').on('click', function(){
        $('#delete').trigger('click');
    });

    // Community detail page
    $('.cd-tab').on('click', function(){
        $('.cd-tab').removeClass('active-cd-tab');
        $('.cd-tab-content').removeClass('active-cd-content');
        $(this).addClass('active-cd-tab');
        $('#cd-tab-' + $(this).data('tab')).addClass('active-cd-content');
    });

    $('#moreBtn').on('click', function(){
        $('.menu').toggle(500);
    });

    $('#commPostBtn').on('click', function(event){
        event.preventDefault();
        var form = document.getElementById('comm');
        var myform = new FormData(form);
        $.ajax({
            url: '/create-comm-post/{{comm.id}}/',
            type: 'POST',
            data: myform,
            success: function(resp){
                console.log(resp);
                document.location.href='/comm_detail/{{comm.id}}/';
            },
            error: function(err){console.log(err);}
        });
    });

    $('.cd-join-btn').on('click', function(){
        var btn = $(this);
        var communityId = btn.data('community-id');
        $.ajax({
            url: '/community/' + communityId + '/join',
            method: 'POST',
            dataType: 'json',
            success: function(resp){
                if(resp.success){
                    if(resp.joined){
                        btn.addClass('active-join');
                        btn.html('<i class="fa-solid fa-check"></i> Joined');
                    } else {
                        btn.removeClass('active-join');
                        btn.html('<i class="fa-solid fa-plus"></i> Join Community');
                    }
                }
            }
        });
    });



    // Global follow widget toggle
    $('.follow-small-btn').on('click', function(){
        var btn = $(this);
        var count = btn.closest('.creator-item').find('.follower-small-btn');
        var num = Number(count.text()) || 0;
        if(btn.hasClass('btn-following')){
            btn.removeClass('btn-following').text('Follow');
            count.text(num - 1);
        } else {
            btn.addClass('btn-following').text('Following');
            count.text(num + 1);
        }
    });




     $('#moreBtn').click(function(){
            $('.menu').toggle(15000)
        })
});
