
import ldap

def ldap_email_lookup(search_name):
    # LDAP server details
    ldap_server = 'ldap.berkeley.edu'
    standard_port = 389
    secure_port = 636
    search_base = 'ou=people,dc=berkeley,dc=edu'
    search_filter = '(cn={})'.format(search_name)
    
    # Establish a connection to the LDAP server
    ldap_conn = ldap.initialize('ldap://{0}:{1}'.format(ldap_server, standard_port))
    
    try:
        # Perform a secure bind using SSL/TLS
        ldap_conn.start_tls_s()
        
        # Search for the email address using the search filter and base
        ldap_result = ldap_conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
        
        # Extract the email address from the search result
        if ldap_result:
            email_address = ldap_result[0][1]['mail'][0].decode('utf-8')
            return email_address
        else:
            return None
    
    except ldap.LDAPError as e:
        print('LDAP Error: {}'.format(e))
    
    finally:
        # Close the LDAP connection
        ldap_conn.unbind()

# Provide the search name
search_name = 'John Doe'

# Call the function to perform the email lookup
email = ldap_email_lookup(search_name)

# Print the result
if email:
    print('Email Address: {}'.format(email))
else:
    print('Email address not found for the given search name.')
