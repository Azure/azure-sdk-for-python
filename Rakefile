#-------------------------------------------------------------------------
# # Copyright (c) Microsoft and contributors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
require 'bundler/gem_tasks'
require 'dotenv/tasks'
require 'rspec/core/rake_task'
require 'open3'
require 'os'

desc 'Azure Resource Manager related tasks which often traverse each of the arm gems'
namespace :arm do
  desc 'Delete ./pkg for each of the Azure Resource Manager projects'
  task :clean do
    each_gem do
      execute_and_stream(OS.windows? ? 'del /S /Q pkg 2>nul' : 'rm -rf ./pkg')
    end
    execute_and_stream(OS.windows? ? 'del /S /Q pkg 2>nul' : 'rm -rf ./pkg')
  end

  desc 'Delete ./lib/generated for each of the Azure Resource Manager projects'
  task :clean_generated do
    each_gem do
      execute_and_stream(OS.windows? ? 'del /S /Q lib\generated 2>nul' : 'rm -rf lib/generated')
    end
  end

  desc 'Build gems for each of the Azure Resource Manager projects'
  task :build => :clean do
    each_gem do
      execute_and_stream('rake build')
    end
    execute_and_stream('rake build')
  end

  desc 'Push gem for each of the Azure Resource Manager projects'
  task :release, [:key] => :build do |_, args|
    each_gem do |dir|
      md = REGEN_METADATA[dir.to_sym]
      # Using execute method so that keys are not logged onto console
      execute("gem push ./pkg/#{dir}-#{md[:version]}.gem" + (args[:key].nil? ? '' : " -k #{args[:key]}"))
    end
    # TODO: Uncomment this when we decide to publish azure_arm gem
    # md = REGEN_METADATA[:azure_arm]
    # Using execute method so that keys are not logged onto console
    # execute("gem push ./pkg/azure_arm-#{md[:version]}.gem" + (args[:key].nil? ? '' : " -k #{args[:key]}"))
  end

  desc 'Regen code for each of the Azure Resource Manager projects'
  task :regen => :clean_generated do
    each_gem do |dir|
      puts "\nGenerating #{dir}\n"
      md = REGEN_METADATA[dir.to_sym]
      ar_base_command = "#{OS.windows? ? '' : 'mono '} #{REGEN_METADATA[:autorest_loc]}"

      if md.is_a?(Array)
        md.each do |sub_md|
          execute_and_stream("#{ar_base_command} -i #{sub_md[:spec_uri]} -pv #{sub_md[:version]} -n #{sub_md[:ns]} -pn #{sub_md[:pn].nil? ? dir : sub_md[:pn]} -g Azure.Ruby -o lib")
        end
      else
        execute_and_stream("#{ar_base_command} -i #{md[:spec_uri]} -pv #{md[:version]} -n #{md[:ns]} -pn #{md[:pn].nil? ? dir : md[:pn]} -g Azure.Ruby -o lib")
      end

    end
  end

  desc 'Bundler related helper'
  namespace :bundle do
    desc 'bundle update for each of the Azure Resource Manager projects'
    task :update do
      each_gem do
        execute_and_stream('bundle update')
      end
    end
  end

  desc 'run specs for each of the Azure Resource Manager projects'
  task :spec => :dotenv do
    each_gem do
      execute_and_stream('bundle install')
      execute_and_stream('bundle exec rspec')
    end
  end
end

task :default => :spec

def execute_and_stream(cmd)
  puts "running: #{cmd}"
  execute(cmd)
end

def execute(cmd)
  Open3.popen2e(cmd) do |_, stdout_err, wait_thr|
    while line = stdout_err.gets
      puts line
    end

    exit_status = wait_thr.value
    unless exit_status.success?
      abort "FAILED !!!"
    end
  end
end

def each_child
  dirs = Dir.entries('./').select { |f| File.directory?(f) and !(f =='.' || f == '..') }
  dirs.each do |dir|
    Dir.chdir(dir) do
      puts "./#{dir}"
      yield(dir)
    end
  end
end

def each_gem
  each_child do |dir|
    if REGEN_METADATA.has_key?(dir.to_sym)
      yield dir
    end
  end
end

version = File.read(File.expand_path('../ARM_VERSION', __FILE__)).strip
REGEN_METADATA = {
    autorest_loc: ENV.fetch('AUTOREST_LOC', '../../../autorest/binaries/net45/AutoRest.exe'),
    azure_arm: {
        version: version,
        tag: 'azure_arm'
    },
    azure_mgmt_authorization: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-authorization/2015-07-01/swagger/authorization.json',
        ns: 'Azure::ARM::Authorization',
        version: version,
        tag: 'arm_auth'
    },
    azure_mgmt_cdn: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-cdn/2016-04-02/swagger/cdn.json',
        ns: 'Azure::ARM::CDN',
        version: version,
        tag: 'arm_cdn'
    },
    azure_mgmt_compute: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/2016-03-30/swagger/compute.json',
        ns: 'Azure::ARM::Compute',
        version: version,
        tag: 'arm_comp'
    },
    azure_mgmt_features: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-resources/features/2015-12-01/swagger/features.json',
        ns: 'Azure::ARM::Features',
        version: version,
        tag: 'arm_feat'
    },
    azure_mgmt_graph: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-graphrbac/1.6-internal/swagger/graphrbac.json',
        ns: 'Azure::ARM::Graph',
        version: version,
        tag: 'arm_grap'
    },
    azure_mgmt_locks: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-resources/locks/2015-01-01/swagger/locks.json',
        ns: 'Azure::ARM::Locks',
        version: version,
        tag: 'arm_lock'
    },
    azure_mgmt_network: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-network/2016-03-30/swagger/network.json',
        ns: 'Azure::ARM::Network',
        version: version,
        tag: 'arm_netw'
    },
    azure_mgmt_notification_hubs: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-notificationhubs/2014-09-01/swagger/notificationhubs.json',
        ns: 'Azure::ARM::NotificationHubs',
        version: version,
        tag: 'arm_noti'
    },
    azure_mgmt_redis: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-redis/2015-08-01/swagger/redis.json',
        ns: 'Azure::ARM::Redis',
        version: version,
        tag: 'arm_redi'
    },
    azure_mgmt_resources: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-resources/resources/2016-02-01/swagger/resources.json',
        ns: 'Azure::ARM::Resources',
        version: version,
        tag: 'arm_reso'
    },
    azure_mgmt_scheduler: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-scheduler/2016-03-01/swagger/scheduler.json',
        ns: 'Azure::ARM::Scheduler',
        version: version,
        tag: 'arm_sche'
    },
    azure_mgmt_search: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-search/2015-02-28/swagger/search.json',
        ns: 'Azure::ARM::Search',
        version: version,
        tag: 'arm_sear'
    },
    azure_mgmt_sql: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-sql/2015-05-01/swagger/sql.json',
        ns: 'Azure::ARM::SQL',
        version: version,
        tag: 'arm_sql'
    },
    azure_mgmt_storage: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-storage/2016-01-01/swagger/storage.json',
        ns: 'Azure::ARM::Storage',
        version: version,
        tag: 'arm_stor'
    },
    azure_mgmt_subscriptions: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-resources/subscriptions/2015-11-01/swagger/subscriptions.json',
        ns: 'Azure::ARM::Subscriptions',
        version: version,
        tag: 'arm_subs'
    },
    azure_mgmt_web: {
        spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-web/2015-08-01/swagger/service.json',
        ns: 'Azure::ARM::Web',
        version: version,
        tag: 'arm_web'
    },
    azure_mgmt_datalake_store: [
        {
            spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-datalake-store/filesystem/2015-10-01-preview/swagger/filesystem.json',
            ns: 'Azure::ARM::DataLakeStore::FileSystem',
            pn: 'azure_mgmt_datalake_store_filesystem',
            tag: 'arm_datalake_store'
        },
        {
            spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-datalake-store/account/2015-10-01-preview/swagger/account.json',
            ns: 'Azure::ARM::DataLakeStore::Account',
            pn: 'azure_mgmt_datalake_store_account',
            # Only the last generated swagger requires version parameter so that we do not override it on AutoRest regeneration code
            version: version,
            tag: 'arm_datalake_store'
        }
    ],
    azure_mgmt_datalake_analytics: [
        {
            spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-datalake-analytics/catalog/2015-10-01-preview/swagger/catalog.json',
            ns: 'Azure::ARM::DataLakeAnalytics::Catalog',
            pn: 'azure_mgmt_datalake_analytics_catalog',
            tag: 'arm_datalake_analytics'
        },
        {
            spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-datalake-analytics/job/2016-03-20-preview/swagger/job.json',
            ns: 'Azure::ARM::DataLakeAnalytics::Job',
            pn: 'azure_mgmt_datalake_analytics_job',
            tag: 'arm_datalake_analytics'
        },
        {
            spec_uri: 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-datalake-analytics/account/2015-10-01-preview/swagger/account.json',
            ns: 'Azure::ARM::DataLakeAnalytics::Account',
            pn: 'azure_mgmt_datalake_analytics_account',
            # Only the last generated swagger requires version parameter so that we do not override it on AutoRest regeneration code
            version: version,
            tag: 'arm_datalake_analytics'
        }
    ],
}
