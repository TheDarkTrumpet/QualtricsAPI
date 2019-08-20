import requests as r
import zipfile
import json
import io
import pandas as pd
from time import gmtime, strftime
from datetime import date
import datetime
from QualtricsAPI.Setup import Credentials
from QualtricsAPI.JSON import Parser

class Distributions(Credentials):
    '''This is a child class to the credentials class and gathers information about  Qualtric's Distributions.'''

    def __init__(self, token=None, directory_id=None, data_center=None):
        self.token = token
        self.data_center = data_center
        self.directory_id = directory_id
        return

    def set_send_date(self, year, month, day, hour='00', minute='00', second='00'):
        '''This method is a helper function to format the send date arguements for several methods in the Distribution Module.
        The send_date parameter must be in the format ""%Y-%m-%dT%H:%M:%SZ" in order for the API to properly parse the send date.

        :param year: The Year for the send_date (e.g. 2000).
        :type year: str
        :param month: The Month for the send_date (e.g. 01, 02, 03, etc.).
        :type month: str
        :param day: The Day for the send_date (e.g. 01, 02, 03, etc.).
        :type day: str
        :param hour: The Hour for the send_date 24-hour clock ['00','23'] (e.g. 01, 02, 03, etc.) Defaulted to '00'.
        :type hour: str
        :param minute: The Minute for the send_date (e.g. 01, 02, 03, etc.) Defaulted to '00'.
        :type minute: str
        :param second: The Second for the send_date (e.g. 01, 02, 03, etc.) Defaulted to '00'.
        :type second: str
        '''

        return f'{year}-{month}-{day}T{hour}:{minute}:{second}Z'



    def create_distribution(self, subject, reply_email, from_email, from_name, mailing_list, library, survey, message, send_date, link_type='Individual'):
        '''This method gives users the ability to create a distribution for a given mailing list and survey. In order to use this method you
        must already have access to pre-defined Messages and their MessageID's existing within a User-Defined (starts with UR_)
        or Global (starts with GR_) Library. You can list the messages and their MessageID's(starts with MS_)  that are available to your user
        account by using the "QualtricsAPI.Library.Messages.list_messages()" method. As a final note, this method gives users the ability to
        define the different types of messages.

        :param subject: The subject for the reminder email.
        :type subject: str
        :param reply_email: The reply email address.
        :type reply_email: str
        :param from_email: The email address that the distribution is sent from.
        :type from_email: str
        :param from_name: The name that shows up on the distribution.
        :type from_name: str
        :param library: The (Global or User) Library ID which the messages are located within.
        :type library: str
        :param message: The Message ID corresponding with the message that is to be sent.
        :type message: str
        :param mailing_list: The Mailing List ID corresponding with the Mailing List that the distribution is to be sent to.
        :type mailing_list: str
        :param survey: The Survey ID corresponding with the Survey that the distribution is to be sent to.
        :type survey: str
        :param send_date: The date that the distribution is supposed to be sent on. Pass gmtime() for immediate distribution or use the set_send_date() method to format properly.
        :type send_date: str
        :param link_type: This parameter refers to the type of link that is to be sent within the distribution.
        :type link_type: str
        '''

        assert len(mailing_list) == 18, 'Hey, the parameter for "mailing_list" that was passed is the wrong length. It should have 18 characters.'
        assert len(library) == 18, 'Hey, the parameter for "library" that was passed is the wrong length. It should have 18 characters.'
        assert len(survey) == 18, 'Hey, the parameter for "survey" that was passed is the wrong length. It should have 18 characters.'
        assert len(message) == 18, 'Hey, the parameter for "message" that was passed is the wrong length. It should have 18 characters.'
        assert mailing_list[:3] == 'CG_', 'Hey there! It looks like your Mailing List ID is incorrect. You can find the Mailing List ID on the Qualtrics site under your account settings. It will begin with "CG_". Please try again.'
        assert survey[:3] == 'SV_', 'Hey there! It looks like your SurveyID is incorrect. You can find the SurveyID on the Qualtrics site under your account settings. It will begin with "SV_". Please try again.'
        assert message[:3] == 'MS_', 'Hey there! It looks like your MessageID is incorrect. You can find the MessageID by using the list messages method available in the Messages module of this Package. It will begin with "MS_". Please try again.'
        assert library[:3] == 'UR_' or library[:3] == 'GR_', 'Hey there! It looks like your Library ID is incorrect. You can find the Library ID on the Qualtrics site under your account settings. It will begin with "UR_" or "GR_". Please try again.'

        try:
            headers, url = self.header_setup(content_type=True, xm=False, path='distributions')
            data = {
                'header': {
                    'fromEmail': from_email,
                    'fromName': from_name,
                    'replyToEmail': reply_email,
                    'subject': subject
                },
                'surveyLink': {
                    'surveyId': survey,
                    'type': 'Individual'
                },
                'recipients': {
                    'mailingListId': mailing_list
                },
                'sendDate': strftime('%Y-%m-%dT%H:%M:%SZ', send_date),
                'message': {
                        'libraryId': library,
                        'messageId': message
                }
            }

            request = r.post(url, json=data, headers=headers)
            response = request.json()
            distribution_id = response['result']['id']
            return distribution_id
        except:
            print(f"\nServerError: QualtricsAPI Error Code: {response['meta']['error']['errorCode']}\nQualtricsAPI Error Message: {response['meta']['error']['errorMessage']}")
        return

    def create_reminder(self, subject, reply_email, from_email, from_name, library, message, distribution, send_date):
        '''This method gives users the ability to create a reminder for a given distribution. In order to create a reminders you must have
        already created a distribution for a given mailing list and survey. Once created, you will pass the Distribution ID corresponding to
        the correct distribution to the distribution parameter and the reminder will be set to that specific distribution. Unlike the
        QualtricsAPI.Survey.Distribution.create_distribution() method, this method does not require you to specify the mailing list or survey
        because it will use the parameters defined when the associated distribution was set up.

        :param subject: The subject for the reminder email.
        :type subject: str
        :param reply_email: The reply email address.
        :type reply_email: str
        :param from_email: The email address that the reminder is sent from.
        :type from_email: str
        :param from_name: The name that shows up on the reminder.
        :type from_name: str
        :param library: The (Global or User) Library ID which the messages are located within.
        :type library: str
        :param message: The Message ID corresponding with the message that is to be sent.
        :type message: str
        :param distribution: The Distribution ID corresponding with the distribution that the reminder is to be attached to.
        :type distribution: str
        :param send_date: The date that the reminder is supposed to be sent on. Pass gmtime() for immediate distribution or use the set_send_date() method to format properly.
        :type send_date: str
        '''

        assert len(distribution) == 19, 'Hey, the parameter for "distribution" that was passed is the wrong length. It should have 19 characters.'
        assert len(library) == 18, 'Hey, the parameter for "library" that was passed is the wrong length. It should have 18 characters.'
        assert len(message) == 18, 'Hey, the parameter for "message" that was passed is the wrong length. It should have 18 characters.'
        assert distribution[:4] == 'EMD_', 'Hey there! It looks like your distributionID is incorrect. You can find the distributionID by using the list_distributions method in this module. It will begin with "UMD_". Please try again.'
        assert message[:3] == 'MS_', 'Hey there! It looks like your MessageID is incorrect. You can find the MessageID by using the list messages method available in the Messages module of this Package. It will begin with "MS_". Please try again.'
        assert library[:3] == 'UR_' or library[:3] == 'GR_', 'Hey there! It looks like your Library ID is incorrect. You can find the Library ID on the Qualtrics site under your account settings. It will begin with "UR_" or "GR_". Please try again.'

        try:
            headers, base_url = self.header_setup(content_type=True, xm=False, path='distributions')
            url = base_url + f'/{distribution}/reminders'
            data = {
                'header': {
                    'fromEmail': from_email,
                    'fromName': from_name,
                    'replyToEmail': reply_email,
                    'subject': subject
                },
                'sendDate': strftime('%Y-%m-%dT%H:%M:%SZ', send_date),
                'message': {
                        'libraryId': library,
                        'messageId': message
                }
            }

            request = r.post(url, json=data, headers=headers)
            response = request.json()
            reminder_id = response['result']
            #Maybe return a success message not the result
            return reminder_id
        except:
            print(f"\nServerError: QualtricsAPI Error Code: {response['meta']['error']['errorCode']}\nQualtricsAPI Error Message: {response['meta']['error']['errorMessage']}")
        return

    def create_thank_you(self, subject, reply_email, from_email, from_name, library, message, distribution, send_date):
        '''This method gives users the ability to create a thank you for a given distribution. In order to create thank you distributions,
         you must have already created a distribution for a given mailing list and survey. Once created, you will pass the Distribution ID
         corresponding to the correct distribution to the distribution parameter and the reminder will be set to that specific distribution.
         Unlike the  QualtricsAPI.Survey.Distribution.create_distribution() method, this method does not require you to specify the mailing
         list or survey because it will use the parameters defined when the associated distribution was set up.

        :param subject: The subject for the reminder email.
        :type subject: str
        :param reply_email: The reply email address.
        :type reply_email: str
        :param from_email: The email address that the reminder is sent from.
        :type from_email: str
        :param from_name: The name that shows up on the reminder.
        :type from_name: str
        :param library: The (Global or User) Library ID which the messages are located within.
        :type library: str
        :param message: The Message ID corresponding with the message that is to be sent.
        :type message: str
        :param distribution: The Distribution ID corresponding with the distribution that the reminder is to be attached to.
        :type distribution: str
        :param send_date: The date that the reminder is supposed to be sent on. Pass gmtime() for immediate distribution or use the set_send_date() method to format properly.
        :type send_date: str
        '''

        assert len(distribution) == 19, 'Hey, the parameter for "distribution" that was passed is the wrong length. It should have 19 characters.'
        assert len(library) == 18, 'Hey, the parameter for "library" that was passed is the wrong length. It should have 18 characters.'
        assert len(message) == 18, 'Hey, the parameter for "message" that was passed is the wrong length. It should have 18 characters.'
        assert distribution[:4] == 'EMD_', 'Hey there! It looks like your distributionID is incorrect. You can find the distributionID by using the list_distributions method in this module. It will begin with "UMD_". Please try again.'
        assert message[:3] == 'MS_', 'Hey there! It looks like your MessageID is incorrect. You can find the MessageID by using the list messages method available in the Messages module of this Package. It will begin with "MS_". Please try again.'
        assert library[:3] == 'UR_' or library[:3] == 'GR_', 'Hey there! It looks like your Library ID is incorrect. You can find the Library ID on the Qualtrics site under your account settings. It will begin with "UR_" or "GR_". Please try again.'

        try:
            headers, base_url = self.header_setup(content_type=True, xm=False, path='distributions')
            url = base_url + f'/{distribution}/thankyous'
            data = {
                'header': {
                    'fromEmail': from_email,
                    'fromName': from_name,
                    'replyToEmail': reply_email,
                    'subject': subject
                },
                'sendDate': strftime('%Y-%m-%dT%H:%M:%SZ', send_date),
                'message': {
                        'libraryId': library,
                        'messageId': message
                }
            }
            request = r.post(url, json=data, headers=headers)
            response = request.json()
            thanks_id = response['result']
            return thanks_id
        except:
            print(f"\nServerError: QualtricsAPI Error Code: {response['meta']['error']['errorCode']}\nQualtricsAPI Error Message: {response['meta']['error']['errorMessage']}")
        return

    def list_distributions(self, survey):
        ''' This method will list all of the distributions corresponding with a given survey. Given that distributions are
        specific to individual surveys, we must pass the SurveyID as an arguement into the survey parameter for this method
        to work appropriately. This method will return a Pandas DataFrame filled with a list of the distributions associated
        with the specific SurveyID passed to the survey parameter.

        :param survey: The Survey ID corresponding with the Survey that the distribution is to be sent to.
        :type survey: str
        :return: A Pandas DataFrame
        '''

        assert survey[:3] == 'SV_', 'Hey there! It looks like your SurveyID is incorrect. You can find the SurveyID on the Qualtrics site under your account settings. It will begin with "SV_". Please try again.'
        assert len(survey) == 18, 'Hey, the parameter for "survey" that was passed is the wrong length. It should have 18 characters.'

        try:
            headers, base_url = self.header_setup(xm=False, path='distributions')
            url = base_url + f'?surveyId={survey}'
            request = r.get(url, headers=headers)
            response = request.json()
            keys = ['id', 'parentDistributionId', 'ownerId', 'organizationId', 'requestStatus', 'requestType',
                    'sendDate', 'createdDate', 'modifiedDate', 'headers', 'fromEmail', 'replyToEmail', 'fromName',
                     'subject', 'recipients', 'mailingListId', 'contactId', 'sampleId', 'message', 'messageId',
                     'messageText', 'surveyLink', 'surveyId', 'expirationDate', 'linkType', 'stats', 'sent', 'failed',
                     'started', 'bounced', 'opened', 'skipped', 'finished', 'complaints', 'blocked']
            dists = Parser().json_parser(response=response, keys=keys, arr=False)
            dist_df = pd.DataFrame(dists).transpose()
            dist_df.columns = keys
            library_ids = Parser().json_parser(response=response, keys=['libraryId'], arr=False)
            dist_df['mailing_list_library_id'] = library_ids[0][:len(dist_df)]
            dist_df['message_library_id'] = library_ids[0][len(dist_df):]
        except:
            print(f"\nServerError: QualtricsAPI Error Code: {response['meta']['error']['errorCode']}\nQualtricsAPI Error Message: {response['meta']['error']['errorMessage']}")
        return dist_df

    def get_distribution(self, survey, distribution):
        ''' This method gives users the ability to get a specific distribution corresponding with a given survey. Given that
        distributions are specific to individual surveys, we must pass the SurveyID as an arguement into the survey parameter for
        this method to work appropriately. This method will return a Pandas DataFrame consisting of multiple variables associated
        with the specified distirbution.

        :param survey: The Survey ID corresponding with the Survey that the distribution is to be sent to.
        :type survey: str
        :param distribution: A specific Distribution ID associated with the given survey.
        :type distribution: str
        :return: A Pandas DataFrame
        '''

        assert survey[:3] == 'SV_', 'Hey there! It looks like your SurveyID is incorrect. You can find the SurveyID on the Qualtrics site under your account settings. It will begin with "SV_". Please try again.'
        assert len(survey) == 18, 'Hey, the parameter for "survey" that was passed is the wrong length. It should have 18 characters.'
        assert len(distribution) == 19, 'Hey, the parameter for "distribution" that was passed is the wrong length. It should have 19 characters.'
        assert distribution[:4] == 'EMD_', 'Hey there! It looks like your distributionID is incorrect. You can find the distributionID by using the list_distributions method in this module. It will begin with "UMD_". Please try again.'

        try:
            headers, base_url = self.header_setup(xm=False, path='distributions')
            url = base_url + f'/{distribution}?surveyId={survey}'
            request = r.get(url, headers=headers)
            response = request.json()
            keys = ['id', 'parentDistributionId', 'ownerId', 'organizationId', 'requestStatus', 'requestType',
                    'sendDate', 'createdDate', 'modifiedDate', 'headers', 'fromEmail', 'replyToEmail', 'fromName',
                     'subject', 'recipients', 'mailingListId', 'contactId', 'sampleId', 'message', 'messageId',
                     'messageText', 'surveyLink', 'surveyId', 'expirationDate', 'linkType', 'stats', 'sent', 'failed',
                     'started', 'bounced', 'opened', 'skipped', 'finished', 'complaints', 'blocked']
            dists = Parser().json_parser(response=response, keys=keys, arr=False)
            dist_df = pd.DataFrame(dists)
            dist_df.index = keys
            library_ids = Parser().json_parser(response=response, keys=['libraryId'], arr=False)
            lib = pd.DataFrame(library_ids[0], index=['mailing_list_library_id', 'message_library_id'])
            dist_df = dist_df.append(lib)
            return dist_df
        except:
            print(f"\nServerError: QualtricsAPI Error Code: {response['meta']['error']['errorCode']}\nQualtricsAPI Error Message: {response['meta']['error']['errorMessage']}")
        return
