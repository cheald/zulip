# Webhooks for external integrations.
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse

from zerver.decorator import api_key_only_webhook_view
from zerver.lib.request import REQ, has_request_variables
from zerver.lib.response import json_success
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile

MESSAGE_TEMPLATE = """
**[{title}]({url})**

```quote
{message}
```

**Project:** {project} ({env})
**Server:** {server}
""".strip()

@api_key_only_webhook_view('Sentry (TTI)')
@has_request_variables
def api_sentry_webhook(request: HttpRequest, user_profile: UserProfile,
                       payload: Dict[str, Any] = REQ(argument_type='body')) -> HttpResponse:
    subject = "{}".format(payload.get('project_name'))
    tags = payload.get("event").get("tags", [])
    tags_dict = {}
    for tag in tags:
        tags_dict[tag[0]] = tag[1]

    body = MESSAGE_TEMPLATE.format(
            title=payload.get("event").get("title"),
            url=payload.get("url"),
            message=payload.get('message'),
            project=payload.get("project"),
            env=payload.get("event").get("environment"),
            server=tags_dict.get("server_name", "unknown")
    )

    check_send_webhook_message(request, user_profile, subject, body)
    return json_success()
