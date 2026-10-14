# Task 2 recovery source registry

Original 13 October failure records outside recovery/ remain unchanged. These records were collected on 14 October 2026 UTC. HTTP 200 alone does not prove post availability. No reviewer handoff has been supplied.

| ID | Requested URL | UTC collection | Origin HTTP / transport | Identity / provenance | Raw SHA-256 |
| --- | --- | --- | --- | --- | --- |
| stanley | https://www.stanley1913.com/ | 2026-10-14T06:35:10.271369+00:00 | 200 / curl 0 | user-approved official website; identity corroborated by branded page and outgoing official accounts | 1890e3bfb615c2a2649f146d8f3b137c3dbfa10dc36d752f0d70e8a4644d12de |
| hydro | https://www.hydroflask.com/ | 2026-10-14T06:35:11.166695+00:00 | 200 / curl 0 | user-approved official website; identity corroborated by branded page and outgoing official accounts | 9eeb2aa4bdc25fd1408599927c93b314616bc5591556b3b176ab834cb537ea26 |
| owala | https://owalalife.com/ | 2026-10-14T06:35:11.480927+00:00 | 200 / curl 0 | user-approved official website; identity corroborated by branded page and outgoing official accounts | 8ed8772e6d16440dad1e11f550b72779f02460ea9a85b738487ce1c85acf8d28 |
| stanley-instagram | https://www.instagram.com/stanley1913_brand/ | 2026-10-14T06:35:12.075919+00:00 | 200 / curl 0 | verified by outgoing link on https://www.stanley1913.com/ | 57f276107323b22939bfefb91434e2c13fecd05062b4a3bbd6aa15372439cc6e |
| stanley-youtube | https://www.youtube.com/@Stanley1913 | 2026-10-14T06:35:12.838963+00:00 | Unavailable (curl 000) / curl 56 | verified by outgoing link on https://www.stanley1913.com/ | No body received |
| hydro-instagram | https://www.instagram.com/hydroflask/ | 2026-10-14T06:35:12.852047+00:00 | 200 / curl 0 | verified by outgoing link on https://www.hydroflask.com/ | a9a87725964943dfb937409ba145aef34ef2ec2759b566bf9748e9a99f515b91 |
| hydro-youtube | https://www.youtube.com/user/hydroflask | 2026-10-14T06:35:13.456338+00:00 | Unavailable (curl 000) / curl 56 | verified by outgoing link on https://www.hydroflask.com/ | No body received |
| owala-instagram | https://www.instagram.com/owala/ | 2026-10-14T06:35:13.469772+00:00 | 200 / curl 0 | verified by outgoing link on https://owalalife.com/ | 7e6b53cca0e1edd7f620171d32e9d8a396d6b8d86b31641aa728b7716f61ad89 |
| owala-youtube | https://www.youtube.com/@owala | 2026-10-14T06:35:14.356231+00:00 | Unavailable (curl 000) / curl 56 | unverified candidate; not an official-account finding | No body received |
| stanley-linkedin | https://www.linkedin.com/company/stanley1913/ | 2026-10-14T06:35:14.368453+00:00 | 999 / curl 0 | unverified candidate; not an official-account finding | 644031a68bde879af85bcc9cb3e6fa1e9a6b0f61d49307581974b5dbc09d3de8 |
| hydro-linkedin | https://www.linkedin.com/company/hydro-flask/ | 2026-10-14T06:35:14.582924+00:00 | 999 / curl 0 | unverified candidate; not an official-account finding | 644031a68bde879af85bcc9cb3e6fa1e9a6b0f61d49307581974b5dbc09d3de8 |
| owala-linkedin | https://www.linkedin.com/company/owala/ | 2026-10-14T06:35:14.740236+00:00 | 999 / curl 0 | unverified candidate; not an official-account finding | 644031a68bde879af85bcc9cb3e6fa1e9a6b0f61d49307581974b5dbc09d3de8 |

## Browser sources

All browser captures are normal unauthenticated pages, without login or access-control bypass. Text records and screenshot digests are in browser_records.json; raw screenshots stay ignored. Instagram has no recovered dated post links. Owala and Instagram assets/CSS loaded incompletely.

| ID | URL | UTC collection | HTTP | Screenshot SHA-256 |
| --- | --- | --- | --- | --- |
| stanley-browser | https://www.stanley1913.com/ | 2026-10-14T06:35:45.144925+00:00 | 200 | 33d3a5f39d8db7062598cfdd28a3f83f0ab1c459f9eeef218aa3522f28b2997d |
| hydro-browser | https://www.hydroflask.com/ | 2026-10-14T06:35:50.078595+00:00 | 200 | 07190c30f34a344358fa3fb184f7d55566f0bec20548fb32456faed6069b5dbc |
| owala-browser | https://owalalife.com/ | 2026-10-14T06:35:53.838467+00:00 | 200 | 65c4f0d59634186b9709c6afbc2b04370996de8fcb2105ede0ebce108f228c81 |
| stanley-instagram-browser | https://www.instagram.com/stanley1913_brand/ | 2026-10-14T06:35:57.262235+00:00 | 200 | 0c72cde6936258ebf25e781267e855d0f5a1d5be1ce90a46bf8d72afd8be2a29 |
| hydro-instagram-browser | https://www.instagram.com/hydroflask/ | 2026-10-14T06:36:00.823394+00:00 | 200 | 426cb3d9c0b40df2164471ccd16bb9352276a6edcd55669e0c7ad702bdb9576e |
| owala-instagram-browser | https://www.instagram.com/owala/ | 2026-10-14T06:36:04.771203+00:00 | 200 | 82de93ac68a88d501e6130b6b35de8dfdbdb39f77c5803ae8fed90d7a4f0ce3c |
