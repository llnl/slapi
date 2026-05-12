# Make sure that user sets SERIES
# There are much better ways to do this, but
# we may not have GNU Make on AIX so
# just force the check for every rule...=(
PYTHONSHORTNAME         = lumosapi-client
PYTHONSHORTPACKAGENAME  = python-$(PYTHONSHORTNAME)
PYTHONVERSION          := $(shell cat PYTHONVERSION)
MODULEVERSION          := $(shell cat MODULEVERSION)
MODULERELEASE          := $(shell cat MODULERELEASE)
PACKAGENAME             = slapi
PACKAGEVERSION         := $(shell cat VERSION)
PACKAGERELEASE         := $(shell cat RELEASE)
GENERATORVERSION       := $(shell cat GENERATORVERSION)
GENERATORURL           := https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/$(GENERATORVERSION)/openapi-generator-cli-$(GENERATORVERSION).jar
BUILDSOURCE             = --buildsource
URL                     = ssh://git@izgitlab.llnl.gov:7999/ssg/$(PACKAGENAME).git
JAVA_HOME              ?= /etc/alternatives/jre_21
PATH                   := $(JAVA_HOME)/bin:$(PATH)

all: $(PACKAGENAME)

.openapi-generator-cli:
	curl --silent --show-error --fail -L $(GENERATORURL) -o ./lib/lumosapi-client/generator/openapi-generator-cli-$(GENERATORVERSION).jar
	touch .openapi-generator-cli

.quilt-lumosapi-client: .openapi-generator-cli
	java -DmaxYamlCodePoints=99999999 -jar ./lib/lumosapi-client/generator/openapi-generator-cli-$(GENERATORVERSION).jar generate --skip-validate-spec -i ./lib/lumosapi-client/api/lumos.spec --inline-schema-options REFACTOR_ALLOF_INLINE_SCHEMAS=true --additional-properties=useOneOfDiscriminatorLookup=true --additional-properties=disallowAdditionalPropertiesIfNotPresent=false -g python -o src/lumosapi_client -p packageName=lumosapi_client -p packageVersion=$(MODULEVERSION)
	./scripts/quilt-lumosapi.pl

$(PACKAGENAME): .quilt-lumosapi-client
	cd src && \
	./autogen.sh && \
	./configure --prefix=/usr PYTHON=python$(PYTHONVERSION) && \
	make -s

.PHONY:
cscope: .PHONY
	rm -f cscope.*
	find ${PWD}/src -name .pc -prune -o -name '*.[chxsS]' -print > cscope.files
	cscope -b -u -k -R

svntag:
	./scripts/svntag.pl $(PACKAGENAME) $(URL)

tag: .PHONY
	@echo Tagging this as $(PACKAGENAME)-$(PACKAGEVERSION)-$(PACKAGERELEASE)
	git tag -a $(PACKAGENAME)-$(PACKAGEVERSION)-$(PACKAGERELEASE) -m "Tagging this as $(PACKAGENAME)-$(PACKAGEVERSION)-$(PACKAGERELEASE)"
	@echo To push your new tag to GitLab run:
	@echo git push origin $(PACKAGENAME)-$(PACKAGEVERSION)-$(PACKAGERELEASE)

tags: .PHONY
	ctags -R --exclude=.pc --exclude=.svn src

rpms-client-release:
	./scripts/build-python-rpm.pl --name $(PYTHONSHORTPACKAGENAME) --pythonversion $(PYTHONVERSION) $(BUILDSOURCE) --scmtype git --scmurl $(URL)

rpms-release:
	./scripts/build-rpm.pl --name $(PACKAGENAME) --pythonversion $(PYTHONVERSION) $(BUILDSOURCE) --scmtype git --scmurl $(URL)

rpms-client: .quilt-lumosapi-client
	./scripts/build-python-rpm.pl --name $(PYTHONSHORTPACKAGENAME) --pythonversion $(PYTHONVERSION) $(BUILDSOURCE) --snapshot -s . -f specs/$(PYTHONSHORTPACKAGENAME).spec

rpms: $(PACKAGENAME)
	./scripts/build-rpm.pl --name $(PACKAGENAME) --pythonversion $(PYTHONVERSION) $(BUILDSOURCE) --snapshot -s . -f specs/$(PACKAGENAME).spec

clean:
	rm -rf .quilt* .openapi-generator-cli tags cscope.*
	rm -rf ./lib/lumosapi-client/generator/openapi-generator-cli*.jar
	cd src && ./autoclean.sh
