# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Logica
# All rights reserved
#
# Author: Nick Piper <nick.piper@logica.com>

from genshi.builder import tag
from trac.core import Component, implements, TracError, ExtensionPoint
from trac.ticket.api import TicketSystem
from trac.resource import Resource
from sidebarplugin.api import ISidebarBoxProvider

class UserTicketsBox(Component):
    implements(ISidebarBoxProvider)

    # ISidebarBoxProvider
    def get_box(self, req):
        if req.authname == "anonymous":
            return

        # hoped that ITicketGroupStatsProvider should tell us what the
        # set of "active" statuses, but seems
        # not. DefaultTicketGroupStatsProvider has an idea, from the
        # ini file, but we want to provide new grouping from the
        # LogicaOrderTracker module so it has to be at the interface
        # level rather than component level.
        
        db = self.env.get_read_db()
        cursor = db.cursor()

        counts_ul = tag.ul()
        cursor.execute("""SELECT status, COUNT(status)
                          FROM ticket
                          WHERE owner = %s
                          GROUP BY status
                          ORDER BY 
                            CASE WHEN status = 'assigned'
                              THEN 1
                              ELSE 0
                            END DESC,
                            CASE WHEN status = 'closed'
                              THEN 1
                              ELSE 0
                            END ASC,
                            status ASC""", (req.authname,))
        for status, count in cursor:
            link = tag(tag.span(class_="ticket-state state-" + status), tag.a(status,href=req.href.query(owner=req.authname,
                                                    status=status)))
            counts_ul.append(tag.li(link, ": ", count))


        recent_ul = tag.ul()
        cursor.execute("""SELECT id
                          FROM ticket
                          WHERE ticket.owner = %s
                          GROUP BY id
                          ORDER BY max(changetime) DESC""", 
                       (req.authname,))
        
        shown_count = 0
        ts = TicketSystem(self.env)
        for ticket,  in cursor:
            resource = Resource('ticket', ticket)
            if "TICKET_VIEW" in req.perm(resource):
                shown_count = shown_count + 1
                if shown_count > 5:
                    break
                compact = ts.get_resource_description(resource, 'compact')
                summary = ts.get_resource_description(resource, 'summary')
                link = tag.a(tag.strong(compact), " ", tag.span(summary), href=req.href.ticket(ticket))
                recent_ul.append(tag.li(link))
       

        return tag(
          tag.div(
            tag.h3(
              tag.i(
                class_="fa fa-ticket"
              ),
            " Your Ticket Counts"
            ),
            counts_ul, class_='box-sidebar color-none', id="sidebar-count"
          ),
          tag.div(
            tag.h3(
              tag.i(
                class_="fa fa-star"
              ),
            " Your Recently Modified Tickets"
            ),
            recent_ul, class_='box-sidebar', id="sidebar-recent"
          )
        )
