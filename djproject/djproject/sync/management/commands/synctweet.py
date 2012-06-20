#/usr/bin/env python
# coding=utf-8

from optparse import make_option
import pprint
pp = pprint.PrettyPrinter(indent=4)

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from djproject.sync.models import SnsAccount, SyncedTweet


class Command(BaseCommand):
    """
    """

    args = u'<user_id user_id ...>'
    help = u'登録されているアカウントのtweetをfacebookに同期します'

    option_list = BaseCommand.option_list + (
        make_option('--dry',
            action='store_true',
            dest='dry',
            default=False,
            help=u'dryrunで実行します'),
    )


    def handle(self, *args, **options):
        """
        """

        '''
        pp.pprint(args)
        pp.pprint(options)
        '''
    
        is_dry = options['dry']

        accounts = SnsAccount.objects.all()

        for account in accounts:
            print "sync [%s] ..." % (account, )
            try:
                account.sync(is_dry)
            except Exception, e:
                print e

# EOF
