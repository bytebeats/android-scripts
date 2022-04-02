
def addFile(fileName):
    fp = open(fileName, 'w')
    fp.write("#Wed Sep 04 11:15:54 CST 2019\n" + "distributionBase=GRADLE_USER_HOME\n" +
             "distributionPath=wrapper/dists\n" + "zipStoreBase=GRADLE_USER_HOME\n" +
             "zipStorePath=wrapper/dists\n" +
             "distributionUrl=https\\://services.gradle.org/distributions/gradle-6.1.1-all.zip")
    fp.close()


if __name__ == '__main__':
    addFile("gradle/wrapper/gradle-wrapper.properties")
    addFile("hotFixPlugin/gradle-plugin/gradle/wrapper/gradle-wrapper.properties")
    addFile("hotFixPlugin/auto-patch-plugin/gradle/wrapper/gradle-wrapper.properties")



