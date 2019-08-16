Permissions
===========

Authorization and permissions are granted based on a user's ``roles`` as
provided by the token sent with each request.

Unauthorized and ``USER`` Role Permissions
------------------------------------------

Users that have not provided a valid JWT or only have the ``USER`` role may
access all resources as read-only.

+-----------------+-------+--------+---------+---------+
| Resource        | List  | Create | Update  | Delete  |
+=================+=======+========+=========+=========+
| Study           | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Release         | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Release Note    | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Task            | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Task Service    | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Event           | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+

``ADMIN`` Role Permissions
--------------------------

Admins have the ability to create and update  most all resources with
excpetion to events, which are generated automatically, and studies, which
are synchronized with studies in the dataservice.

+-----------------+-------+--------+---------+---------+
| Resource        | List  | Create | Update  | Delete  |
+=================+=======+========+=========+=========+
| Study           | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
| Release         | Yes   | Yes    | Yes     | No      |
+-----------------+-------+--------+---------+---------+
| Release Note    | Yes   | Yes    | Yes     | No      |
+-----------------+-------+--------+---------+---------+
| Task            | Yes   | Yes    | Yes     | No      |
+-----------------+-------+--------+---------+---------+
| Task Service    | Yes   | Yes    | Yes     | Yes     |
+-----------------+-------+--------+---------+---------+
| Event           | Yes   | No     | No      | No      |
+-----------------+-------+--------+---------+---------+
