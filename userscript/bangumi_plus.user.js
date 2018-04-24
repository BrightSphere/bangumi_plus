// ==UserScript==
// @name         Bangumi-Plus
// @namespace    https://bangumi.brightsphere.xyz/
// @version      1.0.1
// @author       BrightSphere
// @include      http*://bgm.tv/subject/*
// @include      http*://bangumi.tv/subject/*
// @require      https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js
// @run-at       document-end
// @grant        GM_xmlhttpRequest
// @connect      bangumi.brightsphere.xyz
// @encoding     utf-8
// ==/UserScript==

(function() {
    'use strict';

    var $ = $ || window.$;
    let id = window.location.href.split('/').reverse()[0];
    GM_request(`https://bangumi.brightsphere.xyz/api/subjects/${id}/`).then(JSON.parse).then(data => {
        console.log(data);
        let subjects = '';
        for (let i in data.recommendations) {
            let rmd = data.recommendations[i];
            let subtitle = '';
            if (rmd.auto) {
                subtitle = `相似度${rmd.similarity}`;
            } else {
                subtitle = `${rmd.count}人推荐`;
            }
            let subject = rmd.subject;
            console.log(rmd);
            subjects += `<li>
<span class="sub">${subtitle}</span>
<a href="https://bangumi.brightsphere.xyz/recommendation/${rmd.key}" title="查看详情" class="avatar thumbTip"><span class="avatarNeue avatarSize75" style="background-image:url('${subject.cover.replace('http:','')}')"></span></a>
<a href="/subject/${id}" class="title">${subject.main_name}</a>
</li>`;
        }
        let block = `<div class="subject_section">
<div class="clearit">
<div class="rr"><a href="https://bangumi.brightsphere.xyz/subject/${id}" class="chiiBtn"><span>关联推荐</span></a></div>
<h2 class="subtitle">相关推荐</h2>
</div>
<div class="content_inner">
<ul class="browserCoverMedium clearit">${subjects}</ul>
</div>
</div>`;
        $(".subject_section > .clearit > .subtitle:contains('关联条目')").parent().parent().after(block);
    });


    function GM_request(url, responseType, method) {
        return new Promise(function(resolve, reject) {
            GM_xmlhttpRequest({
                method: method || 'GET',
                url,
                responseType,
                onload: xhr => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(xhr.response);
                    } else {
                        reject(xhr);
                    }
                },
                onerror: xhr => {
                    reject(xhr);
                }
            });
        });
    }
})();