"""
Parses the Jetbrains based IDEs recent projects list
"""

import glob
import os
import xml.etree.ElementTree as ET


class RecentProjectsParser():
    """ Processes the "Recent projects" file from Jetbrains IDEs """
    @staticmethod
    def parse(file_path, query):
        """
        Parses the recent projects file passed as argument and returns a list of projects
        @param str file_path The path to the file which holds the recent open projects by the IDE
        @param str query Optional search query to filter the results
        """
        if not os.path.isfile(file_path):
            return []

        root = ET.parse(file_path).getroot()

        recent_projects = root.findall(  # recent projects in products version 2020.2 and below
            './/component[@name="RecentProjectsManager"][1]/option[@name="recentPaths"]/list/option'
        ) + root.findall(  # recent projects in products version 2020.2 and below
            './/component[@name="RecentDirectoryProjectsManager"][1]/option[@name="recentPaths"]/list/option'
        ) + root.findall(  # projects in groups in products version 2020.3+
            './/component[@name="RecentProjectsManager"][1]/option[@name="groups"]/list/ProjectGroup/option'
            '[@name="projects"]/list/option'
        ) + root.findall(  # recent projects in products version 2020.3+
            './/component[@name="RecentProjectsManager"][1]/option[@name="additionalInfo"]/map/entry'
        )

        home = os.path.expanduser('~')
        query = query.lower() if query else query

        result = []
        already_matched = []
        for project in recent_projects:
            title = ''
            path = (project.attrib['value' if 'value' in project.attrib else 'key']).replace('$USER_HOME$', home)
            name_file = path + '/.idea/.name'

            if os.path.exists(name_file):
                with open(name_file, 'r') as file:
                    title = file.read().replace('\n', '')

            name = os.path.basename(path)
            icons = glob.glob(os.path.join(path, '.idea', 'icon.*'))

            if query and query not in name.lower() and query not in title.lower() and query not in path:
                continue

            # prevent duplicate results, because from version 2020.3, a project can appear more than once in the XML
            # (in the option[@name="groups"] section and in the option[@name="additionalInfo"] section)
            if path in already_matched:
                continue

            already_matched.append(path)

            result.append({
                'name': title or name,
                'path': path,
                'icon': icons[0] if len(icons) > 0 else None
            })

        return result[:8]
