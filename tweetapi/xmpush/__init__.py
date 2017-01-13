# coding=utf-8
from APISender import APISender
from base.APIMessage import *
from base.APIConstants import Constants
from APITools import *
from APISubscribe import *
from tweetapi.config import APP_SECRET
# push-demo
Constants.use_official()
sender = APISender(APP_SECRET)

# build android message
# message = PushMessage() \
#     .restricted_package_name('package_name') \
#     .title('run run run').description('run run run') \
#     .pass_through(0).payload('payload') \
#     .extra({Constants.extra_param_notify_effect: Constants.notify_launcher_activity})
#
# # send message android
# recv = sender.send(message.message_dict(), 'RED_ID')
# print recv


tools = APITools(APP_SECRET)
# print tools.query_message_status('msg_id').data
# print tools.validate_reg_ids(['REG_ID', 'RED_ID1'])
# print tools.query_invalid_reg_ids()
# print tools.query_invalid_aliases()
# print tools.query_device_topics('package_name', 'RED_ID')
# print tools.query_device_presence('package_name', ['REG_ID', 'test'])
# print tools.query_device_aliases('package_name', 'REG_ID')
# print tools.check_schedule_job_exist('tcm111')
subscribe = APISubscribe(APP_SECRET)
# print subscribe.subscribe_topic('RED_ID', 'topic',
#                                 **{Constants.http_param_restricted_package_name: 'package_name'})
# print subscribe.unsubscribe_topic('RED_ID', 'topic',
#                                   **{Constants.http_param_restricted_package_name: 'package_name'})
